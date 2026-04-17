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
  import ReceptorNodeCard from '$lib/components/topology/ReceptorNodeCard.svelte';
  import LayerGroup from '$lib/components/topology/LayerGroup.svelte';
  import type { NodeConfig, ReceptorConfig, Severity } from '$lib/types';
  import { deriveLayers } from '$lib/config-helpers';
  import { signalEvents, nodeHealth, now } from '$lib/stores/signals';
  import { severityRank } from '$lib/util';

  let { data } = $props();

  const nodeTypes = { plexus: PlexusNodeCard, receptor: ReceptorNodeCard, layer: LayerGroup };

  const LAYER_X = 40;
  const LAYER_Y_BASE = 40;
  const LAYER_SPACING = 200;
  const LAYER_WIDTH = 640;
  const LAYER_HEIGHT = 160;

  const RECEPTOR_X = 820;
  const RECEPTOR_Y_BASE = 60;
  const RECEPTOR_SPACING = 110;

  const ACTIVE_EDGE_WINDOW_MS = 1500;

  const sevColor: Record<Severity, string> = {
    info: 'var(--sev-info)',
    notice: 'var(--sev-notice)',
    warning: 'var(--sev-warning)',
    anomaly: 'var(--sev-anomaly)',
    critical: 'var(--sev-critical)'
  };

  function buildFlowNodes(
    nodes: Record<string, NodeConfig>,
    receptors: Record<string, ReceptorConfig>
  ): Node[] {
    const layers = deriveLayers(nodes);
    const out: Node[] = [];

    layers.forEach((layer, idx) => {
      const y = LAYER_Y_BASE + idx * LAYER_SPACING;

      out.push({
        id: `layer-${layer.name}`,
        type: 'layer',
        position: { x: LAYER_X, y },
        data: { label: layer.name.charAt(0).toUpperCase() + layer.name.slice(1), layer: layer.name },
        style: `width: ${LAYER_WIDTH}px; height: ${LAYER_HEIGHT}px;`,
        selectable: false,
        draggable: false,
        zIndex: -1
      });

      layer.nodes.forEach(({ shortId, config }, i) => {
        const count = layer.nodes.length;
        const slot = count === 1 ? LAYER_WIDTH / 2 - 100 : 60 + i * (LAYER_WIDTH - 280);
        out.push({
          id: shortId,
          type: 'plexus',
          parentId: `layer-${layer.name}`,
          extent: 'parent',
          position: { x: slot, y: 50 },
          data: { shortId, node: config }
        });
      });
    });

    Object.entries(receptors).forEach(([receptorId, receptor], i) => {
      out.push({
        id: receptorId,
        type: 'receptor',
        position: { x: RECEPTOR_X, y: RECEPTOR_Y_BASE + i * RECEPTOR_SPACING },
        data: { receptorId, receptor }
      });
    });

    return out;
  }

  const staticEdges = $derived.by<Edge[]>(() => {
    const edges: Edge[] = [];
    for (const [receptorId, receptor] of Object.entries(data.receptors)) {
      for (const nodeId of receptor.listens_to) {
        edges.push({
          id: `${nodeId}->${receptorId}`,
          source: nodeId,
          target: receptorId,
          animated: false,
          style: 'stroke: rgb(var(--border)); stroke-dasharray: 4 4;'
        });
      }
    }
    return edges;
  });

  let nodes: Node[] = $state(buildFlowNodes(data.nodes, data.receptors));
  let edges: Edge[] = $state([]);

  // Reactively light up the edges that are currently carrying signals.
  $effect(() => {
    const cutoff = $now - ACTIVE_EDGE_WINDOW_MS;
    const recent = $signalEvents.filter(
      (e) => new Date(e.signal.timestamp).getTime() >= cutoff
    );

    const lit = new Map<string, Severity>();
    for (const event of recent) {
      for (const result of event.receptor_results) {
        const id = `${event.signal.node_short_id}->${result.receptor_id}`;
        const prev = lit.get(id);
        if (!prev || severityRank(event.signal.severity) > severityRank(prev)) {
          lit.set(id, event.signal.severity);
        }
      }
    }

    const base = staticEdges;
    edges = base.map((e) => {
      const sev = lit.get(e.id);
      if (sev) {
        return {
          ...e,
          animated: true,
          style: `stroke: rgb(${sevColor[sev]}); stroke-width: 2; filter: drop-shadow(0 0 4px rgb(${sevColor[sev]} / 0.6));`
        };
      }
      return { ...e, animated: false, style: 'stroke: rgb(var(--border)); stroke-dasharray: 4 4;' };
    });
  });

  let selection: { kind: 'node' | 'receptor'; id: string } | null = $state(null);

  function onNodeClick({ node: n }: { node: Node }) {
    if (n.type === 'plexus') selection = { kind: 'node', id: n.id };
    else if (n.type === 'receptor') selection = { kind: 'receptor', id: n.id };
    else selection = null;
  }

  const selected = $derived.by(() => {
    if (!selection) return null;
    if (selection.kind === 'node') {
      const node = data.nodes[selection.id];
      if (!node) return null;
      const wired = Object.entries(data.receptors)
        .filter(([, r]) => r.listens_to.includes(selection!.id))
        .map(([id, r]) => ({ id, ...r }));
      return { kind: 'node' as const, shortId: selection.id, node, wired };
    }
    const receptor = data.receptors[selection.id];
    if (!receptor) return null;
    return { kind: 'receptor' as const, receptorId: selection.id, receptor };
  });
</script>

<div class="flex h-full flex-col">
  <header class="flex items-center justify-between border-b border-border bg-surface px-6 py-3">
    <div>
      <h1 class="text-lg font-semibold tracking-wide">Topology</h1>
      <p class="text-xs text-muted">Nodes grouped by layer, wired to receptors via <code class="mono">listens_to</code>. Edges light up as signals flow.</p>
    </div>
  </header>

  <div class="min-h-0 flex-1">
    <SvelteFlow
      bind:nodes
      bind:edges
      {nodeTypes}
      fitView
      proOptions={{ hideAttribution: true }}
      onnodeclick={onNodeClick}
    >
      <Background patternColor="rgb(var(--border))" gap={18} size={1} />
      <Controls showLock={false} />
      <MiniMap
        pannable
        zoomable
        maskColor="rgb(var(--bg) / 0.85)"
        nodeColor={(n) => {
          if (n.type === 'layer') return 'rgb(var(--surface-2))';
          if (n.type === 'receptor') return 'rgb(var(--accent))';
          const h = $nodeHealth[n.id] ?? 'healthy';
          if (h === 'critical') return 'rgb(var(--sev-critical))';
          if (h === 'anomaly') return 'rgb(var(--sev-anomaly))';
          if (h === 'warning') return 'rgb(var(--sev-warning))';
          return 'rgb(var(--sev-healthy))';
        }}
        nodeStrokeColor={(n) => (n.type === 'layer' ? 'rgb(var(--border))' : 'rgb(var(--bg))')}
        nodeStrokeWidth={2}
        nodeBorderRadius={3}
      />
    </SvelteFlow>
  </div>

  {#if selected}
    {@const s = selected}
    <aside class="border-t border-border bg-surface px-6 py-3 text-sm">
      {#if s.kind === 'node'}
        <div class="flex flex-wrap items-center gap-3">
          <span class="font-semibold">{s.shortId}</span>
          <span class="mono text-xs text-muted">{s.node.uuid}</span>
          <span class="chip bg-surface-2 text-muted">{s.node.type}</span>
          <span class="chip bg-surface-2 text-muted">{s.node.layer} layer</span>
          <a href={`/nodes/${s.shortId}`} class="ml-auto text-xs text-accent hover:underline">Open node detail →</a>
        </div>
        <div class="mt-1 text-xs text-muted">{s.node.description}</div>
        {#if s.wired.length > 0}
          <div class="mt-2 text-xs text-muted">
            Wired to:
            {#each s.wired as r, i}
              <a href={`/receptors/${r.id}`} class="ml-1 underline-offset-2 hover:underline">{r.id}</a>{i < s.wired.length - 1 ? ',' : ''}
            {/each}
          </div>
        {/if}
      {:else}
        <div class="flex flex-wrap items-center gap-3">
          <span class="font-semibold">{s.receptorId}</span>
          <span class="mono text-xs text-muted">{s.receptor.uuid}</span>
          <span class="chip bg-surface-2 text-muted">{s.receptor.type}</span>
          <a href={`/receptors/${s.receptorId}`} class="ml-auto text-xs text-accent hover:underline">Open receptor detail →</a>
        </div>
        <div class="mt-1 text-xs text-muted">{s.receptor.description}</div>
        <div class="mt-2 text-xs text-muted">Listens to: {s.receptor.listens_to.join(', ')}</div>
      {/if}
    </aside>
  {/if}
</div>
