import { writable, derived, type Readable } from 'svelte/store';
import type { NodeSummary, Severity, SignalEvent } from '$lib/types';

const MAX_SIGNALS = 500;
const ACTIVE_WINDOW_MS = 10_000;

const SEV_RANK: Record<Severity, number> = {
  info: 0,
  notice: 1,
  warning: 2,
  anomaly: 3,
  critical: 4
};

// ---- Raw signal stream + node registry --------------------------------

export const signalEvents = writable<SignalEvent[]>([]);
export const nodeRegistry = writable<Map<string, NodeSummary>>(new Map());

// Cumulative set of every (pinch_id, action) connection observed since
// page load. Survives the rolling MAX_SIGNALS cap so the predrawn dashed
// routes on the live topology stay visible after the original firing
// event has aged out of `signalEvents`.
export const observedConnections = writable<Set<string>>(new Set());
export const connectionKey = (pinchId: string, action: string) =>
  `${pinchId}|${action}`;

// 1Hz wall-clock so the 10-second windows recompute even when no new
// signals arrive.
export const now = writable(Date.now());
if (typeof window !== 'undefined') {
  setInterval(() => now.set(Date.now()), 1000);
}

export function pushSignal(event: SignalEvent): void {
  signalEvents.update((events) => [event, ...events].slice(0, MAX_SIGNALS));

  nodeRegistry.update((registry) => {
    const prior = registry.get(event.pinch_id);
    registry.set(event.pinch_id, {
      pinch_id: event.pinch_id,
      name: event.name ?? prior?.name ?? null,
      layer: event.layer ?? prior?.layer ?? null,
      source_file: event.source_file,
      source_function: event.source_function,
      last_severity: event.severity,
      last_seen: event.received_at,
      signal_count: (prior?.signal_count ?? 0) + 1
    });
    return new Map(registry);
  });

  if (event.action_result) {
    observedConnections.update((set) => {
      let changed = false;
      for (const action of event.action_result!.actions_fired) {
        const key = connectionKey(event.pinch_id, action);
        if (!set.has(key)) {
          set.add(key);
          changed = true;
        }
      }
      return changed ? new Set(set) : set;
    });
  }
}

export function clearSignals(): void {
  signalEvents.set([]);
  nodeRegistry.set(new Map());
  observedConnections.set(new Set());
}

// ---- Derived views ----------------------------------------------------

export const nodes: Readable<NodeSummary[]> = derived(nodeRegistry, ($registry) =>
  Array.from($registry.values()).sort((a, b) =>
    (a.name ?? a.pinch_id).localeCompare(b.name ?? b.pinch_id)
  )
);

export const nodesByLayer: Readable<Map<string, NodeSummary[]>> = derived(
  nodeRegistry,
  ($registry) => {
    const map = new Map<string, NodeSummary[]>();
    for (const node of $registry.values()) {
      const layer = node.layer ?? 'Undefined';
      if (!map.has(layer)) map.set(layer, []);
      map.get(layer)!.push(node);
    }
    return map;
  }
);

export const layerHealth: Readable<Record<string, Severity>> = derived(
  [signalEvents, now],
  ([$events, $now]) => {
    const cutoff = $now - ACTIVE_WINDOW_MS;
    const recent = $events.filter((e) => e.received_at > cutoff);
    const health: Record<string, Severity> = {};
    for (const e of recent) {
      const layer = e.layer ?? 'Undefined';
      const current = health[layer];
      if (!current || SEV_RANK[e.severity] > SEV_RANK[current]) {
        health[layer] = e.severity;
      }
    }
    return health;
  }
);

export const activeAnomalies: Readable<number> = derived(
  [signalEvents, now],
  ([$events, $now]) => {
    const cutoff = $now - ACTIVE_WINDOW_MS;
    return $events.filter(
      (e) =>
        e.received_at > cutoff &&
        (e.severity === 'anomaly' || e.severity === 'critical')
    ).length;
  }
);

// Only events that fired an action or batch.
export const actionEvents: Readable<SignalEvent[]> = derived(signalEvents, ($events) =>
  $events.filter((e) => e.action_result !== null)
);

// Live stream of "edge fired" events for the topology canvas.
// Each entry is short-lived; topology subscribes and decays them over ~1.5s.
// One edge per action that fired — batches fan out into N edges so every
// action receives its own arrow from the pinch.
export interface LiveEdge {
  id: string;
  source: string; // pinch_id
  target: string; // action-${name}
  severity: Severity;
  fired_at: number;
}

export const liveEdges: Readable<LiveEdge[]> = derived(
  [signalEvents, now],
  ([$events, $now]) => {
    const cutoff = $now - 1500;
    const out: LiveEdge[] = [];
    for (const e of $events) {
      if (!e.action_result || e.received_at < cutoff) continue;
      for (const actionName of e.action_result.actions_fired) {
        const target = `action-${actionName}`;
        out.push({
          id: `${e.pinch_id}->${target}`,
          source: e.pinch_id,
          target,
          severity: e.severity,
          fired_at: e.received_at
        });
      }
    }
    return out;
  }
);

export function signalsForNode(pinchId: string): Readable<SignalEvent[]> {
  return derived(signalEvents, ($events) => $events.filter((e) => e.pinch_id === pinchId));
}
