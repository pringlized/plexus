<script lang="ts">
  import {
    SvelteFlow,
    Background,
    Controls,
    useSvelteFlow,
    type Node,
    type Edge,
    type NodeTypes
  } from '@xyflow/svelte';
  import { ArrowLeft, Check, Cpu, FolderOpen, Save, Zap } from 'lucide-svelte';
  import { statusDot } from '$lib/util';
  import DesignerNodeCard from './DesignerNodeCard.svelte';
  import DesignerActionCard from './DesignerActionCard.svelte';
  import type { DesignerNode, DesignerAction } from './types';
  import SaveViewModal from './SaveViewModal.svelte';
  import LoadViewModal from './LoadViewModal.svelte';
  import FitToContent from '../FitToContent.svelte';

  interface SavedViewSummary {
    id: string;
    name: string;
    description: string | null;
    created_at: string;
    updated_at: string;
  }

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

  const nodeTypes: NodeTypes = {
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

  // ---- Load view -------------------------------------------------------

  let showLoadModal = $state(false);
  let loadingViews = $state(false);
  let loadError: string | null = $state(null);
  let availableViews: SavedViewSummary[] = $state([]);

  async function openLoadModal() {
    showLoadModal = true;
    loadingViews = true;
    loadError = null;
    availableViews = [];
    try {
      const res = await fetch('/api/views');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      availableViews = (await res.json()) as SavedViewSummary[];
    } catch (e) {
      loadError = e instanceof Error ? e.message : String(e);
    } finally {
      loadingViews = false;
    }
  }

  // Approximate rendered card dimensions — used for fit-to-content math.
  // Real measured DOM size would require a ResizeObserver round-trip; these
  // are within a few pixels of actual and good enough for framing.
  const NODE_W = 220;
  const NODE_H = 78;
  const ACTION_W = 200;
  const ACTION_H = 64;

  let canvasEl: HTMLDivElement | undefined = $state();
  let fitTarget: { x: number; y: number; zoom: number } | null = $state(null);

  function fitToNodes(ns: Node[]) {
    if (!canvasEl || ns.length === 0) return;
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;
    for (const n of ns) {
      const w = n.type === 'designerNode' ? NODE_W : ACTION_W;
      const h = n.type === 'designerNode' ? NODE_H : ACTION_H;
      minX = Math.min(minX, n.position.x);
      minY = Math.min(minY, n.position.y);
      maxX = Math.max(maxX, n.position.x + w);
      maxY = Math.max(maxY, n.position.y + h);
    }
    const contentW = Math.max(1, maxX - minX);
    const contentH = Math.max(1, maxY - minY);
    const vw = canvasEl.clientWidth;
    const vh = canvasEl.clientHeight;
    if (vw === 0 || vh === 0) return;
    const padding = 0.1;
    const zoom = Math.min(
      (vw * (1 - padding * 2)) / contentW,
      (vh * (1 - padding * 2)) / contentH,
      1.5
    );
    const x = (vw - contentW * zoom) / 2 - minX * zoom;
    const y = (vh - contentH * zoom) / 2 - minY * zoom;
    fitTarget = { x, y, zoom };
  }

  async function handleLoadSelected(view: SavedViewSummary) {
    loadingViews = true;
    loadError = null;
    try {
      const res = await fetch(`/api/views/${view.id}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const full = (await res.json()) as {
        id: string;
        name: string;
        layout_json: {
          nodes: { pinch_id: string; position: { x: number; y: number } }[];
          actions: { name: string; position: { x: number; y: number } }[];
        };
      };

      const restored: Node[] = [];
      for (const n of full.layout_json.nodes ?? []) {
        const def = FAKE_NODES.find((x) => x.pinch_id === n.pinch_id);
        if (!def) continue;
        restored.push({
          id: nextId('node', n.pinch_id),
          type: 'designerNode',
          position: n.position,
          data: { node: def }
        });
      }
      for (const a of full.layout_json.actions ?? []) {
        const def = FAKE_ACTIONS.find((x) => x.name === a.name);
        if (!def) continue;
        restored.push({
          id: nextId('action', a.name),
          type: 'designerAction',
          position: a.position,
          data: { action: def }
        });
      }

      nodes = restored;
      savedView = { id: full.id, name: full.name };
      showLoadModal = false;

      // Defer fit until the new nodes have laid out and the canvas knows its size.
      queueMicrotask(() => fitToNodes(restored));
    } catch (e) {
      loadError = e instanceof Error ? e.message : String(e);
    } finally {
      loadingViews = false;
    }
  }

  // ---- Save view -------------------------------------------------------

  let savedView: { id: string; name: string } | null = $state(null);
  let showSaveModal = $state(false);
  let saving = $state(false);
  let saveError: string | null = $state(null);

  function buildLayout() {
    const nodeItems = nodes.filter((n) => n.type === 'designerNode');
    const actionItems = nodes.filter((n) => n.type === 'designerAction');
    return {
      nodes: nodeItems.map((n) => ({
        pinch_id: (n.data as any).node.pinch_id as string,
        position: n.position
      })),
      actions: actionItems.map((n) => ({
        name: (n.data as any).action.name as string,
        position: n.position
      }))
    };
  }

  async function handleSave({
    name,
    description
  }: {
    name: string;
    description: string;
  }) {
    saving = true;
    saveError = null;
    try {
      const layout = buildLayout();
      let res: Response;
      if (savedView) {
        res = await fetch(`/api/views/${savedView.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, description, layout_json: layout })
        });
      } else {
        res = await fetch('/api/views', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, description, layout_json: layout })
        });
      }
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.error ?? `HTTP ${res.status}`);
      }
      if (savedView) {
        savedView = { id: savedView.id, name };
      } else {
        const body = await res.json();
        savedView = { id: body.id, name: body.name };
      }
      showSaveModal = false;
    } catch (e) {
      saveError = e instanceof Error ? e.message : String(e);
    } finally {
      saving = false;
    }
  }

  // ---- Drag and drop ---------------------------------------------------

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

  <!-- Save button + saved indicator (top-right overlay) -->
  <div class="absolute right-3 top-3 z-30 flex items-center gap-2">
    {#if savedView}
      <span
        class="inline-flex items-center gap-1 rounded-md border border-sev-healthy/40 bg-sev-healthy/10 px-2 py-1 text-xs text-sev-healthy shadow-sm"
        title={`Saved as ${savedView.name}`}
      >
        <Check size={12} />
        {savedView.name}
      </span>
    {/if}
    <button
      type="button"
      onclick={openLoadModal}
      class="inline-flex items-center gap-1 rounded-md border border-border bg-surface px-3 py-1 text-xs font-medium text-text shadow-sm transition hover:border-accent/60 hover:text-accent"
    >
      <FolderOpen size={12} />
      Load Topology
    </button>
    <button
      type="button"
      onclick={() => (showSaveModal = true)}
      disabled={nodes.length === 0}
      class="inline-flex items-center gap-1 rounded-md border border-accent/40 bg-accent/10 px-3 py-1 text-xs font-medium text-accent shadow-sm transition hover:border-accent hover:bg-accent/20 disabled:cursor-not-allowed disabled:opacity-40"
    >
      <Save size={12} />
      {savedView ? 'Update View' : 'Save View'}
    </button>
  </div>

  {#if showLoadModal}
    <LoadViewModal
      views={availableViews}
      loading={loadingViews}
      error={loadError}
      onload={handleLoadSelected}
      oncancel={() => {
        showLoadModal = false;
        loadError = null;
      }}
    />
  {/if}

  {#if showSaveModal}
    <SaveViewModal
      initialName={savedView?.name ?? ''}
      {saving}
      error={saveError}
      onsave={handleSave}
      oncancel={() => {
        showSaveModal = false;
        saveError = null;
      }}
    />
  {/if}

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
    bind:this={canvasEl}
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
      initialViewport={{ x: 40, y: 40, zoom: 0.85 }}
      minZoom={0.25}
      maxZoom={2}
      ondelete={onDelete}
      proOptions={{ hideAttribution: true }}
    >
      <FitToContent target={fitTarget} />
      <Background patternColor="rgb(var(--border))" gap={20} size={1} />
      <Controls showLock={false} />
    </SvelteFlow>
  </div>
</div>
