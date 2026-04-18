<script lang="ts">
  import {
    SvelteFlow,
    Background,
    Controls,
    MiniMap,
    type Node,
    type Edge,
    type NodeTypes
  } from '@xyflow/svelte';
  import { ArrowLeft, FolderOpen } from 'lucide-svelte';
  import PlexusNodeCard from '$lib/components/topology/PlexusNodeCard.svelte';
  import ActionNodeCard from '$lib/components/topology/ActionNodeCard.svelte';
  import LayerGroup from '$lib/components/topology/LayerGroup.svelte';
  import FitToContent from '$lib/components/topology/FitToContent.svelte';
  import LoadViewModal from '$lib/components/topology/LoadViewModal.svelte';
  import {
    nodes as nodeStore,
    nodesByLayer,
    nodeRegistry,
    liveEdges,
    observedConnections
  } from '$lib/stores/signals';
  import type { NodeSummary, ActionConfig } from '$lib/types';

  interface SavedViewSummary {
    id: string;
    name: string;
    description: string | null;
    created_at: string;
    updated_at: string;
  }
  interface SavedLayout {
    nodes: { pinch_id: string; position: { x: number; y: number } }[];
    actions: { name: string; position: { x: number; y: number } }[];
    connections?: { pinch_id: string; action: string }[];
  }

  let { data } = $props();

  const nodeTypes: NodeTypes = {
    plexus: PlexusNodeCard,
    action: ActionNodeCard,
    layer: LayerGroup
  };

  // Layout constants
  const LAYER_X = 40;
  const LAYER_Y_BASE = 40;
  const LAYER_SPACING = 200;
  const LAYER_WIDTH = 700;
  const LAYER_HEIGHT = 160;

  const PINCH_SLOT_W = 220;
  const PINCH_Y = 50;

  const ACTION_X = 840;
  const ACTION_SPACING = 80;
  const ACTION_CARD_HEIGHT = 60;

  function buildFlowNodes(
    byLayer: Map<string, NodeSummary[]>,
    actions: ActionConfig[]
  ): Node[] {
    const out: Node[] = [];

    // Layer groups + pinch nodes inside
    Array.from(byLayer.entries()).forEach(([layer, layerNodes], idx) => {
      const y = LAYER_Y_BASE + idx * LAYER_SPACING;
      out.push({
        id: `layer-${layer}`,
        type: 'layer',
        position: { x: LAYER_X, y },
        data: { label: layer.charAt(0).toUpperCase() + layer.slice(1), layer },
        style: `width: ${LAYER_WIDTH}px; height: ${LAYER_HEIGHT}px;`,
        selectable: false,
        draggable: false,
        zIndex: -1
      });

      layerNodes.forEach((n, i) => {
        out.push({
          id: n.pinch_id,
          type: 'plexus',
          parentId: `layer-${layer}`,
          extent: 'parent',
          position: { x: 30 + i * PINCH_SLOT_W, y: PINCH_Y },
          data: { node: n }
        });
      });
    });

    // Action nodes — stacked vertically and centered on the layer column
    // so live edges from any pinch converge into a tight middle band.
    const layerCount = Math.max(1, byLayer.size);
    const layerAreaTop = LAYER_Y_BASE;
    const layerAreaBottom = LAYER_Y_BASE + (layerCount - 1) * LAYER_SPACING + LAYER_HEIGHT;
    const layerAreaCenter = (layerAreaTop + layerAreaBottom) / 2;

    const actionStackHeight =
      (actions.length - 1) * ACTION_SPACING + ACTION_CARD_HEIGHT;
    const actionStartY = layerAreaCenter - actionStackHeight / 2;

    actions.forEach((a, i) => {
      out.push({
        id: `action-${a.name}`,
        type: 'action',
        position: { x: ACTION_X, y: actionStartY + i * ACTION_SPACING },
        data: { action: a }
      });
    });

    return out;
  }

  const sevColor: Record<string, string> = {
    info: 'var(--sev-info)',
    notice: 'var(--sev-notice)',
    warning: 'var(--sev-warning)',
    anomaly: 'var(--sev-anomaly)',
    critical: 'var(--sev-critical)'
  };

  // ---- Saved-view overlay --------------------------------------------
  // When the user loads a topology view, we replace the auto-derived
  // layout with the saved one. Cards still hydrate from the live signal
  // stream (nodeRegistry / data.actions) so colors, pulses and edges all
  // keep firing — only the geometry is frozen.

  const NODE_W = 220;
  const ACTION_W = 200;

  let loadedView = $state<{ id: string; name: string } | null>(null);
  let loadedLayout = $state<SavedLayout | null>(null);

  function buildSavedFlowNodes(layout: SavedLayout): Node[] {
    const out: Node[] = [];
    const registry = $nodeRegistry;

    for (const ln of layout.nodes) {
      const live = registry.get(ln.pinch_id);
      const node: NodeSummary = live ?? {
        pinch_id: ln.pinch_id,
        name: null,
        layer: null,
        source_file: '',
        source_function: '(awaiting first signal)',
        last_severity: 'info',
        last_seen: 0,
        signal_count: 0
      };
      out.push({
        id: ln.pinch_id,
        type: 'plexus',
        position: ln.position,
        data: { node },
        draggable: false,
        selectable: false
      });
    }

    for (const la of layout.actions) {
      const action: ActionConfig = data.actions.find((a) => a.name === la.name) ?? {
        name: la.name,
        enabled: false
      };
      out.push({
        id: `action-${la.name}`,
        type: 'action',
        position: la.position,
        data: { action },
        draggable: false,
        selectable: false
      });
    }

    return out;
  }

  const flowNodes = $derived(
    loadedLayout
      ? buildSavedFlowNodes(loadedLayout)
      : buildFlowNodes($nodesByLayer, data.actions)
  );

  // Predrawn dashed edges. In saved-view mode they come from the stored
  // connection list; in live mode they accumulate from every (node, action)
  // pair observed since page load. Sit underneath the animated live edges
  // so each firing lights up its existing dashed route.
  const dashedEdges = $derived.by<Edge[]>(() => {
    const style = 'stroke: #534AB7; stroke-width: 1; stroke-dasharray: 4 3;';
    if (loadedLayout) {
      const conns = loadedLayout.connections ?? [];
      return conns.map((c, i) => ({
        id: `dash-${c.pinch_id}-${c.action}-${i}`,
        source: c.pinch_id,
        target: `action-${c.action}`,
        type: 'default',
        animated: false,
        style
      }));
    }
    return Array.from($observedConnections).map((key) => {
      const [pinch, action] = key.split('|');
      return {
        id: `dash-${pinch}-${action}`,
        source: pinch,
        target: `action-${action}`,
        type: 'default',
        animated: false,
        style
      };
    });
  });
  const dynamicEdges = $derived(
    $liveEdges.map((e) => ({
      id: `live-${e.id}-${e.fired_at}`,
      source: e.source,
      target: e.target,
      animated: true,
      style: `stroke: rgb(${sevColor[e.severity]}); stroke-width: 2; filter: drop-shadow(0 0 4px rgb(${sevColor[e.severity]} / 0.6));`
    }))
  );

  // Initialize with current derived values so SvelteFlow's fitView has
  // real content to fit on first mount (empty arrays mount → bad zoom).
  let nodes: Node[] = $state(flowNodes);
  let edges: Edge[] = $state(dynamicEdges);
  $effect(() => {
    nodes = flowNodes;
  });
  $effect(() => {
    edges = [...dashedEdges, ...dynamicEdges];
  });

  // Manual fit-to-content: compute the bounding box from known dimensions
  // and the live layer count, then push a viewport that frames it. Runs
  // whenever a new layer emerges or the action set changes — does NOT
  // run on every pinch (which keeps user pan/zoom intact between events).
  let canvasEl: HTMLDivElement | undefined = $state();

  const targetViewport = $derived.by(() => {
    if (!canvasEl) return null;
    const vw = canvasEl.clientWidth;
    const vh = canvasEl.clientHeight;
    if (vw === 0 || vh === 0) return null;

    let left: number, right: number, top: number, bottom: number;

    if (loadedLayout) {
      // Bounding box of every saved item.
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      for (const n of loadedLayout.nodes) {
        minX = Math.min(minX, n.position.x);
        minY = Math.min(minY, n.position.y);
        maxX = Math.max(maxX, n.position.x + NODE_W);
        maxY = Math.max(maxY, n.position.y + 78);
      }
      for (const a of loadedLayout.actions) {
        minX = Math.min(minX, a.position.x);
        minY = Math.min(minY, a.position.y);
        maxX = Math.max(maxX, a.position.x + ACTION_W);
        maxY = Math.max(maxY, a.position.y + 64);
      }
      if (!isFinite(minX)) return null;
      left = minX; right = maxX; top = minY; bottom = maxY;
    } else {
      const layerCount = Math.max(1, $nodesByLayer.size);
      const actionCount = Math.max(1, data.actions.length);
      const layersTop = LAYER_Y_BASE;
      const layersBottom = LAYER_Y_BASE + (layerCount - 1) * LAYER_SPACING + LAYER_HEIGHT;
      const actionsHeight = (actionCount - 1) * ACTION_SPACING + ACTION_CARD_HEIGHT;
      top = Math.min(layersTop, (layersTop + layersBottom) / 2 - actionsHeight / 2);
      bottom = Math.max(layersBottom, (layersTop + layersBottom) / 2 + actionsHeight / 2);
      left = LAYER_X;
      right = ACTION_X + 200;
    }

    const contentW = Math.max(1, right - left);
    const contentH = Math.max(1, bottom - top);
    const padding = 0.08;
    const zoom = Math.min(
      (vw * (1 - padding * 2)) / contentW,
      (vh * (1 - padding * 2)) / contentH,
      1.0
    );
    const x = (vw - contentW * zoom) / 2 - left * zoom;
    const y = (vh - contentH * zoom) / 2 - top * zoom;
    return { x, y, zoom };
  });

  // ---- Load-view modal ------------------------------------------------
  //
  // The list always starts with a synthetic "Default Topology" entry that
  // routes back to the live (auto-grouped) view. The currently displayed
  // view — either the synthetic default or a saved one — is shown
  // disabled in the modal so the user can see what they're already on.

  const DEFAULT_VIEW_ID = '__default__';
  const defaultViewEntry: SavedViewSummary = {
    id: DEFAULT_VIEW_ID,
    name: 'Default Topology',
    description: 'Live layer view — nodes auto-group by layer as signals arrive.',
    created_at: '',
    updated_at: ''
  };

  let showLoadModal = $state(false);
  let loadingViews = $state(false);
  let loadError: string | null = $state(null);
  let savedViews: SavedViewSummary[] = $state([]);

  const modalViews = $derived([defaultViewEntry, ...savedViews]);
  const currentViewId = $derived(loadedView ? loadedView.id : DEFAULT_VIEW_ID);

  async function openLoadModal() {
    showLoadModal = true;
    loadingViews = true;
    loadError = null;
    savedViews = [];
    try {
      const res = await fetch('/api/views');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      savedViews = (await res.json()) as SavedViewSummary[];
    } catch (e) {
      loadError = e instanceof Error ? e.message : String(e);
    } finally {
      loadingViews = false;
    }
  }

  async function handleLoadSelected(view: SavedViewSummary) {
    if (view.id === DEFAULT_VIEW_ID) {
      returnToLive();
      showLoadModal = false;
      return;
    }
    loadingViews = true;
    loadError = null;
    try {
      const res = await fetch(`/api/views/${view.id}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const full = (await res.json()) as { id: string; name: string; layout_json: SavedLayout };
      loadedLayout = full.layout_json;
      loadedView = { id: full.id, name: full.name };
      showLoadModal = false;
    } catch (e) {
      loadError = e instanceof Error ? e.message : String(e);
    } finally {
      loadingViews = false;
    }
  }

  function returnToLive() {
    loadedView = null;
    loadedLayout = null;
  }
</script>

<div class="flex h-full flex-col">
  <header class="flex items-center justify-between border-b border-border bg-surface px-6 py-3">
    <div>
      <h1 class="text-lg font-semibold tracking-wide">
        Topology
        {#if loadedView}
          <span class="ml-2 text-xs font-normal text-muted">·</span>
          <span class="ml-1 text-sm font-medium text-accent">{loadedView.name}</span>
        {/if}
      </h1>
      <p class="text-xs text-muted">
        {#if loadedView}
          Saved view · read-only. Live signals still drive node colors and edge animations.
        {:else}
          Live nodes (left) auto-register from the signal stream. Actions (right)
          come from <code class="mono">plexus-actions.yaml</code>. Edges light up
          as actions fire — batches fan out into one edge per action.
        {/if}
      </p>
    </div>
    <div class="flex items-center gap-2">
      {#if loadedView}
        <button
          type="button"
          onclick={returnToLive}
          class="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-muted transition hover:border-accent/60 hover:text-text"
        >
          <ArrowLeft size={12} />
          Live View
        </button>
      {/if}
      <button
        type="button"
        onclick={openLoadModal}
        class="inline-flex items-center gap-1.5 rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-text transition hover:border-accent/60 hover:text-accent"
      >
        <FolderOpen size={12} />
        Load Topology
      </button>
      <a
        href="/topology/custom/new"
        class="inline-flex items-center gap-1.5 rounded-md border border-accent/40 bg-accent/10 px-3 py-1.5 text-xs font-medium text-accent transition hover:border-accent hover:bg-accent/20"
      >
        + Custom Topology
      </a>
    </div>
  </header>

  {#if showLoadModal}
    <LoadViewModal
      views={modalViews}
      currentId={currentViewId}
      loading={loadingViews}
      error={loadError}
      onload={handleLoadSelected}
      oncancel={() => {
        showLoadModal = false;
        loadError = null;
      }}
    />
  {/if}

  <div bind:this={canvasEl} class="relative min-h-0 flex-1">
    {#if !loadedLayout && $nodeStore.length === 0}
      <div class="absolute inset-0 z-10 flex items-center justify-center pointer-events-none">
        <div class="rounded-lg border border-border bg-surface px-6 py-4 text-sm text-muted shadow-lg">
          Waiting for first signal…
        </div>
      </div>
    {/if}
    <SvelteFlow
      bind:nodes
      bind:edges
      {nodeTypes}
      initialViewport={{ x: 20, y: 20, zoom: 0.55 }}
      minZoom={0.25}
      maxZoom={1.5}
      nodesDraggable={!loadedLayout}
      nodesConnectable={false}
      elementsSelectable={!loadedLayout}
      proOptions={{ hideAttribution: true }}
    >
      <FitToContent target={targetViewport} />
      <Background patternColor="rgb(var(--border))" gap={18} size={1} />
      <Controls showLock={false} />
      <MiniMap
        pannable
        zoomable
        maskColor="rgb(var(--bg) / 0.85)"
        nodeColor={(n) => {
          if (n.type === 'layer') return 'rgb(var(--surface-2))';
          if (n.type === 'action') return 'rgb(var(--accent))';
          return 'rgb(var(--sev-healthy))';
        }}
        nodeStrokeColor={() => 'rgb(var(--bg))'}
        nodeStrokeWidth={2}
        nodeBorderRadius={3}
      />
    </SvelteFlow>
  </div>
</div>
