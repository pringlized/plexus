import {
  NODES,
  RECEPTORS,
  glassglyphPayload,
  authPayload,
  ingestionPayload,
  embeddingPayload,
  buildPayload,
  pipelinePayload
} from './fixtures';
import type {
  LayerHealth,
  LayerId,
  PlexusNode,
  Receipt,
  Receptor,
  ReceptorAction,
  Severity,
  Signal
} from './types';

const MAX_SIGNALS = 500;
const MAX_RECEIPTS = 300;
const MAX_ACTIONS = 120;
const ACTIVE_WINDOW_MS = 10_000;

const SEVERITY_RANK: Record<Severity, number> = {
  info: 0,
  notice: 1,
  warning: 2,
  anomaly: 3,
  critical: 4
};

const uid = () =>
  globalThis.crypto?.randomUUID?.() ??
  `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;

// ---- Reactive state ---------------------------------------------------

export const sim = $state({
  signals: [] as Signal[], // newest first
  receipts: [] as Receipt[], // newest first
  actions: [] as ReceptorAction[], // newest first
  paused: false,
  queuedWhilePaused: 0,
  totalToday: 0,
  criticalToday: 0,
  anomalyToday: 0,
  started: false,
  now: Date.now() // ticked so relative timestamps re-render
});

export const nodes: PlexusNode[] = NODES;
export const receptors: Receptor[] = RECEPTORS;

// ---- Derived helpers --------------------------------------------------

export function recentSignalsForNode(nodeId: string, windowMs = ACTIVE_WINDOW_MS): Signal[] {
  const cutoff = sim.now - windowMs;
  return sim.signals.filter((s) => s.node_id === nodeId && s.timestamp >= cutoff);
}

export function nodeHealth(nodeId: string): LayerHealth {
  const recent = recentSignalsForNode(nodeId);
  let max: LayerHealth = 'healthy';
  for (const s of recent) {
    if (s.severity === 'critical') return 'critical';
    if (s.severity === 'anomaly' && max !== 'critical') max = 'anomaly';
    if (s.severity === 'warning' && max === 'healthy') max = 'warning';
  }
  return max;
}

export function layerHealth(layer: LayerId): LayerHealth {
  const layerNodes = nodes.filter((n) => n.layer === layer);
  let worst: LayerHealth = 'healthy';
  for (const n of layerNodes) {
    const h = nodeHealth(n.id);
    if (h === 'critical') return 'critical';
    if (h === 'anomaly' && worst !== 'critical') worst = 'anomaly';
    if (h === 'warning' && worst === 'healthy') worst = 'warning';
  }
  return worst;
}

export function activeAnomalies(): number {
  let count = 0;
  for (const n of nodes) {
    const h = nodeHealth(n.id);
    if (h === 'anomaly' || h === 'critical') count++;
  }
  return count;
}

export function receptorsFor(signal: Signal): Receptor[] {
  return receptors.filter((r) => receptorMatches(r, signal));
}

function receptorMatches(r: Receptor, signal: Signal): boolean {
  const nodeOk = r.listensTo === '*' || r.listensTo.includes(signal.node_id);
  const sevOk = r.firesOn === '*' || r.firesOn.includes(signal.severity);
  return nodeOk && sevOk;
}

export function signalsByNode(nodeId: string, limit = 50): Signal[] {
  return sim.signals.filter((s) => s.node_id === nodeId).slice(0, limit);
}

export function receiptsByReceptor(receptorId: string, limit = 50): Receipt[] {
  return sim.receipts.filter((r) => r.receptor_id === receptorId).slice(0, limit);
}

export function actionsByReceptor(receptorId: string, limit = 50): ReceptorAction[] {
  return sim.actions.filter((a) => a.receptor_id === receptorId).slice(0, limit);
}

export function severityRank(s: Severity): number {
  return SEVERITY_RANK[s];
}

// ---- Emission engine --------------------------------------------------

const sequences = new Map<string, number>();

function nextSequence(nodeId: string): number {
  const s = (sequences.get(nodeId) ?? 0) + 1;
  sequences.set(nodeId, s);
  return s;
}

function pushCapped<T>(arr: T[], item: T, max: number) {
  arr.unshift(item);
  if (arr.length > max) arr.length = max;
}

function emit(nodeId: string, severity: Severity, category: string, payload: Record<string, unknown>) {
  if (sim.paused) {
    sim.queuedWhilePaused += 1;
    return;
  }
  const node = nodes.find((n) => n.id === nodeId)!;
  const signal: Signal = {
    signal_id: uid(),
    node_id: node.id,
    node_type: node.type,
    timestamp: Date.now(),
    severity,
    category,
    payload,
    system_layer: node.layer,
    sequence: nextSequence(node.id)
  };
  pushCapped(sim.signals, signal, MAX_SIGNALS);

  sim.totalToday += 1;
  if (severity === 'critical') sim.criticalToday += 1;
  if (severity === 'anomaly') sim.anomalyToday += 1;

  // Fan-out to receptors.
  for (const r of receptorsFor(signal)) {
    const summary = receiptSummary(r, severity);
    const receipt: Receipt = {
      id: uid(),
      receptor_id: r.id,
      signal_id: signal.signal_id,
      node_id: signal.node_id,
      severity,
      timestamp: Date.now(),
      ok: true,
      summary
    };
    pushCapped(sim.receipts, receipt, MAX_RECEIPTS);

    // Meaningful actions: agent-invoker dispatches.
    if (r.type === 'agent-invoker') {
      const action: ReceptorAction = {
        id: uid(),
        receptor_id: r.id,
        signal_id: signal.signal_id,
        node_id: signal.node_id,
        timestamp: Date.now(),
        action: 'Agent dispatched',
        status: 'pending',
        detail: `Triggered by ${node.name} / ${severity}. Signal: ${category}.`
      };
      pushCapped(sim.actions, action, MAX_ACTIONS);

      // Resolve after ~1.1s.
      const duration = 950 + Math.floor(Math.random() * 400);
      setTimeout(() => {
        const target = sim.actions.find((a) => a.id === action.id);
        if (!target) return;
        target.status = 'completed';
        target.duration_ms = duration;
        target.detail = 'Security specialist invoked. Document quarantined. Incident logged.';
      }, duration);
    }
    // Alerter gets a lightweight action row for warnings+.
    if (r.type === 'alerter' && SEVERITY_RANK[severity] >= SEVERITY_RANK.anomaly) {
      const action: ReceptorAction = {
        id: uid(),
        receptor_id: r.id,
        signal_id: signal.signal_id,
        node_id: signal.node_id,
        timestamp: Date.now(),
        action: 'Alert sent',
        status: 'completed',
        detail: `Vector channel notified. Severity: ${severity}.`,
        duration_ms: 80 + Math.floor(Math.random() * 60)
      };
      pushCapped(sim.actions, action, MAX_ACTIONS);
    }
  }
}

function receiptSummary(r: Receptor, severity: Severity): string {
  switch (r.type) {
    case 'alerter':
      return severity === 'critical' ? 'critical alert dispatched' : `${severity} alert dispatched`;
    case 'logger':
      return 'logged';
    case 'health-aggregator':
      return 'layer health updated';
    case 'agent-invoker':
      return 'agent dispatch queued';
    case 'threshold-watcher':
      return 'threshold evaluated';
  }
}

// ---- Per-node scheduling ---------------------------------------------

type Scheduler = () => void;
const timers: ReturnType<typeof setTimeout>[] = [];

function schedule(fn: Scheduler, minMs: number, maxMs: number) {
  const delay = minMs + Math.random() * (maxMs - minMs);
  const t = setTimeout(() => {
    try {
      fn();
    } finally {
      schedule(fn, minMs, maxMs);
    }
  }, delay);
  timers.push(t);
}

function startNodeSchedulers() {
  // glassglyph-scanner-01 — mostly clean
  schedule(() => emit('node-001', 'info', 'scan.clean', glassglyphPayload('info')), 4000, 8000);
  schedule(() => emit('node-001', 'anomaly', 'bidi.override_detected', glassglyphPayload('anomaly')), 30000, 45000);

  // auth-monitor-01 — low activity
  schedule(() => emit('node-002', 'info', 'auth.session_ok', authPayload('info')), 12000, 20000);
  schedule(() => emit('node-002', 'warning', 'auth.unusual_pattern', authPayload('warning')), 120000, 180000);

  // ma-ingestion-01 — steady info, anomaly occasionally
  schedule(() => emit('node-003', 'info', 'document.received', ingestionPayload('info')), 3000, 6000);
  schedule(() => emit('node-003', 'anomaly', 'pipeline.stall', ingestionPayload('anomaly')), 150000, 210000);

  // embedding-pipeline-01
  schedule(() => emit('node-004', 'info', 'document.embedded', embeddingPayload()), 5000, 10000);

  // buildengine-01
  schedule(
    () =>
      emit(
        'node-005',
        Math.random() < 0.08 ? 'warning' : 'notice',
        Math.random() < 0.08 ? 'stage.slow' : 'dependency.resolved',
        buildPayload(Math.random() < 0.08 ? 'warning' : 'notice')
      ),
    15000,
    25000
  );

  // pipeline-monitor-01
  schedule(() => emit('node-006', 'notice', 'stage.transition', pipelinePayload()), 10000, 18000);

  // The critical cascade — every 85–95s.
  schedule(
    () => emit('node-001', 'critical', 'invisible.unicode_encoding', glassglyphPayload('critical')),
    85000,
    95000
  );
}

// Clock tick — keeps "X ago" timestamps reactive and recomputes derived health.
function startClock() {
  const t = setInterval(() => {
    sim.now = Date.now();
  }, 1000);
  timers.push(t as unknown as ReturnType<typeof setTimeout>);
}

// Priming — give the UI something to look at on first paint.
function primeHistory() {
  // Back-date a handful of signals so the feed isn't empty.
  const seeds: Array<[string, Severity, string, () => Record<string, unknown>]> = [
    ['node-003', 'info', 'document.received', () => ingestionPayload('info')],
    ['node-004', 'info', 'document.embedded', () => embeddingPayload()],
    ['node-001', 'info', 'scan.clean', () => glassglyphPayload('info')],
    ['node-005', 'notice', 'dependency.resolved', () => buildPayload('notice')],
    ['node-006', 'notice', 'stage.transition', () => pipelinePayload()],
    ['node-003', 'info', 'document.received', () => ingestionPayload('info')],
    ['node-001', 'info', 'scan.clean', () => glassglyphPayload('info')],
    ['node-002', 'info', 'auth.session_ok', () => authPayload('info')]
  ];
  seeds.forEach(([n, s, c, p], i) => {
    const node = nodes.find((x) => x.id === n)!;
    const signal: Signal = {
      signal_id: uid(),
      node_id: n,
      node_type: node.type,
      timestamp: Date.now() - (seeds.length - i) * 1500,
      severity: s,
      category: c,
      payload: p(),
      system_layer: node.layer,
      sequence: nextSequence(n)
    };
    pushCapped(sim.signals, signal, MAX_SIGNALS);
    sim.totalToday += 1;
  });
}

export function startSimulation() {
  if (sim.started || typeof window === 'undefined') return;
  sim.started = true;
  primeHistory();
  startNodeSchedulers();
  startClock();
}

export function togglePause() {
  sim.paused = !sim.paused;
  if (!sim.paused) sim.queuedWhilePaused = 0;
}
