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
  import BatchNodeCard from '$lib/components/topology/BatchNodeCard.svelte';
  import LayerGroup from '$lib/components/topology/LayerGroup.svelte';
  import {
    nodes as nodeStore,
    nodesByLayer,
    liveEdges,
    layerHealth
  } from '$lib/stores/signals';
  import type { NodeSummary, ActionConfig, BatchConfig } from '$lib/types';

  let { data } = $props();

  const nodeTypes = {
    plexus: PlexusNodeCard,
    action: ActionNodeCard,
    batch: BatchNodeCard,
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

  const ACTION_X = 800;
  const ACTION_Y_BASE = 60;
  const ACTION_SPACING = 80;

  const BATCH_X = 1050;
  const BATCH_Y_BASE = 60;
  const BATCH_SPACING = 90;

  function buildFlowNodes(
    byLayer: Map<string, NodeSummary[]>,
    actions: ActionConfig[],
    batches: BatchConfig[]
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

    // Action nodes
    actions.forEach((a, i) => {
      out.push({
        id: `action-${a.name}`,
        type: 'action',
        position: { x: ACTION_X, y: ACTION_Y_BASE + i * ACTION_SPACING },
        data: { action: a }
      });
    });

    // Batch nodes
    batches.forEach((b, i) => {
      out.push({
        id: `batch-${b.name}`,
        type: 'batch',
        position: { x: BATCH_X, y: BATCH_Y_BASE + i * BATCH_SPACING },
        data: { batch: b }
      });
    });

    return out;
  }

  // Static edges: batch → each action it contains.
  function buildStaticEdges(batches: BatchConfig[]): Edge[] {
    const edges: Edge[] = [];
    for (const b of batches) {
      for (const actionName of b.actions) {
        edges.push({
          id: `static-${b.name}->${actionName}`,
          source: `batch-${b.name}`,
          target: `action-${actionName}`,
          animated: false,
          style: 'stroke: rgb(var(--border)); stroke-dasharray: 3 3; stroke-width: 1;'
        });
      }
    }
    return edges;
  }

  const sevColor: Record<string, string> = {
    info: 'var(--sev-info)',
    notice: 'var(--sev-notice)',
    warning: 'var(--sev-warning)',
    anomaly: 'var(--sev-anomaly)',
    critical: 'var(--sev-critical)'
  };

  const flowNodes = $derived(buildFlowNodes($nodesByLayer, data.actions, data.batches));
  const staticEdges = $derived(buildStaticEdges(data.batches));
  const dynamicEdges = $derived(
    $liveEdges.map((e) => ({
      id: `live-${e.id}-${e.fired_at}`,
      source: e.source,
      target: e.target,
      animated: true,
      style: `stroke: rgb(${sevColor[e.severity]}); stroke-width: 2; filter: drop-shadow(0 0 4px rgb(${sevColor[e.severity]} / 0.6));`
    }))
  );
  const flowEdges = $derived([...staticEdges, ...dynamicEdges]);

  let nodes: Node[] = $state([]);
  let edges: Edge[] = $state([]);
  $effect(() => {
    nodes = flowNodes;
  });
  $effect(() => {
    edges = flowEdges;
  });
</script>

<div class="flex h-full flex-col">
  <header class="flex items-center justify-between border-b border-border bg-surface px-6 py-3">
    <div>
      <h1 class="text-lg font-semibold tracking-wide">Topology</h1>
      <p class="text-xs text-muted">
        Live nodes (left) auto-register from the signal stream. Actions and batches
        (right) come from <code class="mono">plexus-actions.yaml</code>. Edges light up as batches fire.
      </p>
    </div>
  </header>

  <div class="relative min-h-0 flex-1">
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
      fitView
      proOptions={{ hideAttribution: true }}
    >
      <Background patternColor="rgb(var(--border))" gap={18} size={1} />
      <Controls showLock={false} />
      <MiniMap
        pannable
        zoomable
        maskColor="rgb(var(--bg) / 0.85)"
        nodeColor={(n) => {
          if (n.type === 'layer') return 'rgb(var(--surface-2))';
          if (n.type === 'action' || n.type === 'batch') return 'rgb(var(--accent))';
          return 'rgb(var(--sev-healthy))';
        }}
        nodeStrokeColor={() => 'rgb(var(--bg))'}
        nodeStrokeWidth={2}
        nodeBorderRadius={3}
      />
    </SvelteFlow>
  </div>
</div>
