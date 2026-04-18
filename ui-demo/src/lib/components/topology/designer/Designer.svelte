<script lang="ts">
  import {
    SvelteFlow,
    Background,
    Controls,
    useSvelteFlow,
    type Node,
    type Edge
  } from '@xyflow/svelte';
  import { ArrowLeft, Cpu, Zap } from 'lucide-svelte';
  import { statusDot } from '$lib/util';
  import DesignerNodeCard, { type DesignerNode } from './DesignerNodeCard.svelte';
  import DesignerActionCard, { type DesignerAction } from './DesignerActionCard.svelte';

  // ---- Fake data (will be live in a future revision) -------------------

  const FAKE_NODES: DesignerNode[] = [
    {
      pinch_id: 'f375a1d08ad1',
      name: 'Security scan critical',
      layer: 'security',
      source_function: 'scan_critical',
      last_severity: 'critical'
    },
    {
      pinch_id: '23d806cbd927',
      name: 'Security scan clean',
      layer: 'security',
      source_function: 'scan_clean',
      last_severity: 'info'
    },
    {
      pinch_id: 'd80b689fb5be',
      name: 'Health service down',
      layer: 'health',
      source_function: 'health_service_down',
      last_severity: 'critical'
    },
    {
      pinch_id: 'd6d1f99156ff',
      name: 'Health heartbeat',
      layer: 'health',
      source_function: 'health_heartbeat',
      last_severity: 'info'
    },
    {
      pinch_id: 'b24b424c7544',
      name: 'Build stage failed',
      layer: 'build',
      source_function: 'build_failed',
      last_severity: 'critical'
    },
    {
      pinch_id: '4b1ac77ae5fb',
      name: 'Build dependency resolved',
      layer: 'build',
      source_function: 'build_dep_resolved',
      last_severity: 'info'
    },
    {
      pinch_id: 'd8fdfe9b5a57',
      name: 'Ingestion document received',
      layer: 'ingestion',
      source_function: 'ingest_received',
      last_severity: 'info'
    },
    {
      pinch_id: '4d70e277e6f3',
      name: 'Ingestion pipeline stalled',
      layer: 'ingestion',
      source_function: 'ingest_stalled',
      last_severity: 'anomaly'
    },
    {
      pinch_id: '2541390539b6',
      name: 'Agent task pickup',
      layer: 'agent',
      source_function: 'agent_task_pickup',
      last_severity: 'info'
    },
    {
      pinch_id: 'aef98ac95c65',
      name: 'Redis server unreachable',
      layer: 'servers',
      source_function: 'redis_down',
      last_severity: 'critical'
    }
  ];

  const FAKE_ACTIONS: DesignerAction[] = [
    { name: 'dispatch-security-agent', enabled: true },
    { name: 'reboot-redis-server', enabled: true },
    { name: 'notify-telegram', enabled: true },
    { name: 'invoke-ops-agent', enabled: true },
    { name: 'log-critical-event', enabled: true }
  ];

  const CONNECTION_MAP: Record<string, string[]> = {
    f375a1d08ad1: ['dispatch-security-agent', 'notify-telegram'],
    d80b689fb5be: ['reboot-redis-server', 'notify-telegram'],
    b24b424c7544: ['notify-telegram'],
    '4d70e277e6f3': ['dispatch-security-agent'],
    aef98ac95c65: ['reboot-redis-server', 'invoke-ops-agent'],
    '2541390539b6': ['invoke-ops-agent'],
    d8fdfe9b5a57: ['log-critical-event'],
    '23d806cbd927': [],
    d6d1f99156ff: [],
    '4b1ac77ae5fb': []
  };

  // ---- Canvas state ----------------------------------------------------
  //
  // `nodes` is the single source of truth — SvelteFlow binds to it two-way
  // (drag to reposition, click to select, Delete to remove). We mutate it
  // directly on drop/delete rather than recomputing from a derived store,
  // so the viewport never jumps around on structural changes.

  const nodeTypes = {
    designerNode: DesignerNodeCard,
    designerAction: DesignerActionCard
  };

  let nodes: Node[] = $state([]);
  let instanceCounter = 0;

  function nextId(prefix: string, key: string): string {
    instanceCounter += 1;
    return `${prefix}-${key}-${instanceCounter}`;
  }

  // Introspect a Flow node to learn its kind and key (pinch_id or action name).
  function nodeKey(n: Node): { kind: 'node' | 'action'; key: string } | null {
    if (n.type === 'designerNode' && n.data && (n.data as any).node)
      return { kind: 'node', key: (n.data as any).node.pinch_id };
    if (n.type === 'designerAction' && n.data && (n.data as any).action)
      return { kind: 'action', key: (n.data as any).action.name };
    return null;
  }

  // Counts of each item on the canvas for the palette badges.
  const nodeCounts = $derived.by(() => {
    const counts: Record<string, number> = {};
    for (const n of nodes) {
      const k = nodeKey(n);
      if (k?.kind === 'node') counts[k.key] = (counts[k.key] ?? 0) + 1;
    }
    return counts;
  });
  const actionCounts = $derived.by(() => {
    const counts: Record<string, number> = {};
    for (const n of nodes) {
      const k = nodeKey(n);
      if (k?.kind === 'action') counts[k.key] = (counts[k.key] ?? 0) + 1;
    }
    return counts;
  });

  // Auto-wire: every node-instance × every action-instance whose pair is in
  // the connection map gets an edge. Edges recompute whenever `nodes`
  // changes (drop, delete). Drop order doesn't matter.
  const edges = $derived.by<Edge[]>(() => {
    const nodeInstances = nodes.filter((n) => n.type === 'designerNode');
    const actionInstances = nodes.filter((n) => n.type === 'designerAction');
    const out: Edge[] = [];
    for (const n of nodeInstances) {
      const pinchId = (n.data as any).node.pinch_id as string;
      const wired = CONNECTION_MAP[pinchId] ?? [];
      for (const a of actionInstances) {
        const actionName = (a.data as any).action.name as string;
        if (wired.includes(actionName)) {
          out.push({
            id: `${n.id}->${a.id}`,
            source: n.id,
            target: a.id,
            type: 'smoothstep',
            animated: false,
            style: 'stroke: #534AB7; stroke-width: 1; stroke-dasharray: 4 3;'
          });
        }
      }
    }
    return out;
  });

  // ---- Drag and drop ---------------------------------------------------

  const { screenToFlowPosition } = useSvelteFlow();

  function onPaletteDragStart(
    e: DragEvent,
    payload: { kind: 'node' | 'action'; key: string }
  ) {
    if (!e.dataTransfer) return;
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('application/plexus-designer', JSON.stringify(payload));
  }

  function onCanvasDragOver(e: DragEvent) {
    e.preventDefault();
    if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy';
  }

  function onCanvasDrop(e: DragEvent) {
    e.preventDefault();
    const raw = e.dataTransfer?.getData('application/plexus-designer');
    if (!raw) return;
    let payload: { kind: 'node' | 'action'; key: string };
    try {
      payload = JSON.parse(raw);
    } catch {
      return;
    }
    const position = screenToFlowPosition({ x: e.clientX, y: e.clientY });
    const id = nextId(payload.kind, payload.key);

    if (payload.kind === 'node') {
      const node = FAKE_NODES.find((n) => n.pinch_id === payload.key);
      if (!node) return;
      nodes.push({
        id,
        type: 'designerNode',
        position,
        data: { node }
      });
    } else {
      const action = FAKE_ACTIONS.find((a) => a.name === payload.key);
      if (!action) return;
      nodes.push({
        id,
        type: 'designerAction',
        position,
        data: { action }
      });
    }
  }

  // SvelteFlow's built-in Delete/Backspace already removed the items from
  // `nodes` before this fires; we mostly accept it. We *don't* replace
  // `nodes` — that would reset viewport / drag state.
  function onDelete(_: { nodes?: Node[]; edges?: Edge[] }) {
    // no-op — bound `nodes` was already mutated by SvelteFlow. Edges
    // auto-recompute via $derived.
  }
</script>

<div class="relative flex h-screen w-screen overflow-hidden bg-bg text-text">
  <!-- Back arrow overlay (top-left, above palette boundary) -->
  <a
    href="/topology"
    class="absolute left-3 top-3 z-30 inline-flex items-center gap-1 rounded-md border border-border bg-surface px-2.5 py-1 text-xs text-muted shadow-sm transition hover:text-text"
  >
    <ArrowLeft size={12} />
    Back
  </a>

  <!-- Palette (left, fixed width, scrollable) -->
  <aside class="z-20 flex h-full w-56 shrink-0 flex-col border-r border-border bg-surface pt-12">
    <div class="px-3 pb-2 text-[10px] uppercase tracking-widest text-muted">Custom Topology</div>

    <div class="flex-1 overflow-y-auto px-2 pb-4">
      <div class="px-1 pt-2 text-[10px] uppercase tracking-widest text-muted">Nodes</div>
      <ul class="mt-1 space-y-1">
        {#each FAKE_NODES as n (n.pinch_id)}
          {@const count = nodeCounts[n.pinch_id] ?? 0}
          <li>
            <button
              type="button"
              draggable="true"
              ondragstart={(e) => onPaletteDragStart(e, { kind: 'node', key: n.pinch_id })}
              class="group flex w-full cursor-grab items-center gap-2 rounded-md border border-border bg-surface-2 px-2 py-1.5 text-left text-xs transition hover:border-accent/60 active:cursor-grabbing
                {count > 0 ? 'opacity-60' : ''}"
              title={`${n.source_function} · ${n.layer}`}
            >
              <span class="inline-block h-1.5 w-1.5 rounded-full {statusDot(n.last_severity)}"></span>
              <Cpu size={11} class="text-muted" />
              <div class="min-w-0 flex-1">
                <div class="truncate text-[11.5px] font-medium">{n.name}</div>
                <div class="truncate text-[9.5px] text-muted">{n.layer}</div>
              </div>
              {#if count > 0}
                <span class="rounded bg-accent/20 px-1 text-[9px] text-accent">{count}</span>
              {/if}
            </button>
          </li>
        {/each}
      </ul>

      <div class="mt-4 px-1 text-[10px] uppercase tracking-widest text-muted">Actions</div>
      <ul class="mt-1 space-y-1">
        {#each FAKE_ACTIONS as a (a.name)}
          {@const count = actionCounts[a.name] ?? 0}
          <li>
            <button
              type="button"
              draggable="true"
              ondragstart={(e) => onPaletteDragStart(e, { kind: 'action', key: a.name })}
              class="group flex w-full cursor-grab items-center gap-2 rounded-md border border-border bg-surface-2 px-2 py-1.5 text-left text-xs transition hover:border-accent/60 active:cursor-grabbing
                {count > 0 ? 'opacity-60' : ''}"
            >
              <Zap size={11} class="text-accent" />
              <div class="min-w-0 flex-1 truncate text-[11.5px] font-medium">{a.name}</div>
              {#if count > 0}
                <span class="rounded bg-accent/20 px-1 text-[9px] text-accent">{count}</span>
              {/if}
            </button>
          </li>
        {/each}
      </ul>
    </div>
  </aside>

  <!-- Canvas (drop target) -->
  <div
    class="relative flex-1"
    role="region"
    ondragover={onCanvasDragOver}
    ondrop={onCanvasDrop}
  >
    {#if nodes.length === 0}
      <div class="absolute inset-0 z-10 flex items-center justify-center pointer-events-none">
        <div class="rounded-lg border border-dashed border-border bg-surface/70 px-6 py-4 text-sm text-muted shadow-lg">
          Drag nodes and actions from the palette
        </div>
      </div>
    {/if}

    <SvelteFlow
      bind:nodes
      {edges}
      {nodeTypes}
      defaultViewport={{ x: 40, y: 40, zoom: 0.85 }}
      minZoom={0.25}
      maxZoom={2}
      ondelete={onDelete}
      proOptions={{ hideAttribution: true }}
    >
      <Background patternColor="rgb(var(--border))" gap={20} size={1} />
      <Controls showLock={false} />
    </SvelteFlow>
  </div>
</div>
