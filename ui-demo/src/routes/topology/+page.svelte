<script lang="ts">
  import {
    SvelteFlow,
    Background,
    Controls,
    MiniMap,
    type Node,
    type Edge
  } from '@xyflow/svelte';
  import PlexusNodeCard from '$lib/components/topology/PlexusNodeCard.svelte';
  import ActionNodeCard from '$lib/components/topology/ActionNodeCard.svelte';
  import LayerGroup from '$lib/components/topology/LayerGroup.svelte';
  import FitToContent from '$lib/components/topology/FitToContent.svelte';
  import {
    nodes as nodeStore,
    nodesByLayer,
    liveEdges
  } from '$lib/stores/signals';
  import type { NodeSummary, ActionConfig } from '$lib/types';

  let { data } = $props();

  const nodeTypes = {
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

  const flowNodes = $derived(buildFlowNodes($nodesByLayer, data.actions));
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
    edges = dynamicEdges;
  });

  // Manual fit-to-content: compute the bounding box from known dimensions
  // and the live layer count, then push a viewport that frames it. Runs
  // whenever a new layer emerges or the action set changes — does NOT
  // run on every pinch (which keeps user pan/zoom intact between events).
  let canvasEl: HTMLDivElement | undefined = $state();

  const targetViewport = $derived.by(() => {
    if (!canvasEl) return null;
    const layerCount = Math.max(1, $nodesByLayer.size);
    const actionCount = Math.max(1, data.actions.length);

    // Bounding box of all canvas content.
    const layersTop = LAYER_Y_BASE;
    const layersBottom = LAYER_Y_BASE + (layerCount - 1) * LAYER_SPACING + LAYER_HEIGHT;
    const actionsHeight = (actionCount - 1) * ACTION_SPACING + ACTION_CARD_HEIGHT;
    const top = Math.min(layersTop, (layersTop + layersBottom) / 2 - actionsHeight / 2);
    const bottom = Math.max(layersBottom, (layersTop + layersBottom) / 2 + actionsHeight / 2);

    const left = LAYER_X;
    const right = ACTION_X + 200; // action card width

    const contentW = right - left;
    const contentH = bottom - top;

    const vw = canvasEl.clientWidth;
    const vh = canvasEl.clientHeight;
    if (vw === 0 || vh === 0) return null;

    const padding = 0.08;
    const zoomFitW = (vw * (1 - padding * 2)) / contentW;
    const zoomFitH = (vh * (1 - padding * 2)) / contentH;
    const zoom = Math.min(zoomFitW, zoomFitH, 1.0);

    // Center the bounding box in the viewport.
    const x = (vw - contentW * zoom) / 2 - left * zoom;
    const y = (vh - contentH * zoom) / 2 - top * zoom;

    return { x, y, zoom };
  });
</script>

<div class="flex h-full flex-col">
  <header class="flex items-center justify-between border-b border-border bg-surface px-6 py-3">
    <div>
      <h1 class="text-lg font-semibold tracking-wide">Topology</h1>
      <p class="text-xs text-muted">
        Live nodes (left) auto-register from the signal stream. Actions (right)
        come from <code class="mono">plexus-actions.yaml</code>. Edges light up
        as actions fire — batches fan out into one edge per action.
      </p>
    </div>
  </header>

  <div bind:this={canvasEl} class="relative min-h-0 flex-1">
    {#if $nodeStore.length === 0}
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
      defaultViewport={{ x: 20, y: 20, zoom: 0.55 }}
      minZoom={0.25}
      maxZoom={1.5}
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
