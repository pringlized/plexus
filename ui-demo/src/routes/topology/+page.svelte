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
  import { nodes as plexusNodes, receptors as plexusReceptors, sim, receptorsFor, severityRank, nodeHealth } from '$lib/sim/store.svelte';
  import { LAYERS } from '$lib/sim/fixtures';
  import type { Severity } from '$lib/sim/types';

  const nodeTypes = { plexus: PlexusNodeCard, receptor: ReceptorNodeCard, layer: LayerGroup };

  const NODE_X = 260;
  const NODE_COL_SPACING = 240;
  const ROW_HEIGHT = 210;
  const ROW_TOP = 60;
  const NODE_Y_IN_ROW = 50;
  const RECEPTOR_X = 900;

  // Layer band group nodes
  const layerBands: Node[] = LAYERS.map((l, idx) => ({
    id: `layer-${l.id}`,
    type: 'layer',
    position: { x: 40, y: ROW_TOP + idx * ROW_HEIGHT },
    data: { label: l.name, layer: l.id },
    style: `width: ${NODE_X + 2 * NODE_COL_SPACING}px; height: ${ROW_HEIGHT - 20}px;`,
    selectable: false,
    draggable: false,
    zIndex: -1
  }));

  // Plexus nodes — two per layer row
  const nodeNodes: Node[] = plexusNodes.map((n) => {
    const layerIdx = LAYERS.findIndex((l) => l.id === n.layer);
    const inLayer = plexusNodes.filter((x) => x.layer === n.layer);
    const col = inLayer.findIndex((x) => x.id === n.id);
    return {
      id: n.id,
      type: 'plexus',
      position: {
        x: NODE_X + col * NODE_COL_SPACING,
        y: ROW_TOP + layerIdx * ROW_HEIGHT + NODE_Y_IN_ROW
      },
      data: { node: n }
    };
  });

  // Receptor nodes stacked on the right
  const receptorNodes: Node[] = plexusReceptors.map((r, i) => ({
    id: r.id,
    type: 'receptor',
    position: { x: RECEPTOR_X, y: ROW_TOP + i * 110 + 20 },
    data: { receptor: r }
  }));

  // Static edges: each node → each matching receptor
  const staticEdges: Edge[] = [];
  for (const n of plexusNodes) {
    for (const r of plexusReceptors) {
      const listens = r.listensTo === '*' || r.listensTo.includes(n.id);
      if (!listens) continue;
      staticEdges.push({
        id: `${n.id}->${r.id}`,
        source: n.id,
        target: r.id,
        animated: false,
        style: 'stroke: rgb(var(--border)); stroke-dasharray: 4 4;'
      });
    }
  }

  let nodes: Node[] = $state([...layerBands, ...nodeNodes, ...receptorNodes]);
  let edges: Edge[] = $state(staticEdges);

  // Live edge animation: react to recent signals and toggle edge style for ~1.2s.
  const sevColor: Record<Severity, string> = {
    info: 'var(--sev-info)',
    notice: 'var(--sev-notice)',
    warning: 'var(--sev-warning)',
    anomaly: 'var(--sev-anomaly)',
    critical: 'var(--sev-critical)'
  };

  $effect(() => {
    const cutoff = sim.now - 1500;
    const activeSignals = sim.signals.filter((s) => s.timestamp >= cutoff);
    // Determine which edges are currently "lit".
    const litEdges = new Map<string, Severity>();
    for (const s of activeSignals) {
      for (const r of receptorsFor(s)) {
        const id = `${s.node_id}->${r.id}`;
        const prev = litEdges.get(id);
        if (!prev || severityRank(s.severity) > severityRank(prev)) {
          litEdges.set(id, s.severity);
        }
      }
    }
    edges = staticEdges.map((e) => {
      const sev = litEdges.get(e.id);
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

  // Selected node/receptor for detail drawer.
  let selection: { kind: 'node' | 'receptor'; id: string } | null = $state(null);
  function onNodeClick({ node: n }: { node: Node }) {
    if (n.type === 'plexus') selection = { kind: 'node', id: n.id };
    else if (n.type === 'receptor') selection = { kind: 'receptor', id: n.id };
    else selection = null;
  }

  const selected = $derived(() => {
    if (!selection) return null;
    if (selection.kind === 'node') {
      const n = plexusNodes.find((x) => x.id === selection.id);
      if (!n) return null;
      const wired = plexusReceptors.filter((r) => r.listensTo === '*' || r.listensTo.includes(n.id));
      const last = sim.signals.find((s) => s.node_id === n.id);
      return { kind: 'node' as const, node: n, wired, last };
    }
    const r = plexusReceptors.find((x) => x.id === selection!.id);
    if (!r) return null;
    const last = sim.receipts.find((rc) => rc.receptor_id === r.id);
    return { kind: 'receptor' as const, receptor: r, last };
  });
</script>

<div class="flex h-full flex-col">
  <header class="flex items-center justify-between border-b border-border bg-surface px-6 py-3">
    <div>
      <h1 class="text-lg font-semibold tracking-wide">Topology</h1>
      <p class="text-xs text-muted">Nodes (left) wired to receptors (right). Edges light up as signals flow.</p>
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
          const h = nodeHealth(n.id);
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

  {#if selected()}
    {@const s = selected()!}
    <aside class="border-t border-border bg-surface px-6 py-3 text-sm">
      {#if s.kind === 'node'}
        <div class="flex flex-wrap items-center gap-3">
          <span class="font-semibold">{s.node.name}</span>
          <span class="mono text-xs text-muted">{s.node.id}</span>
          <span class="chip bg-surface-2 text-muted">{s.node.type}</span>
          <span class="chip bg-surface-2 text-muted">{s.node.layer} layer</span>
          <a href={`/nodes/${s.node.id}`} class="ml-auto text-xs text-accent hover:underline">Open node detail →</a>
        </div>
        <div class="mt-1 text-xs text-muted">{s.node.description}</div>
        <div class="mt-2 text-xs text-muted">
          Wired to:
          {#each s.wired as r, i}
            <a href={`/receptors/${r.id}`} class="ml-1 underline-offset-2 hover:underline">{r.name}</a>{i < s.wired.length - 1 ? ',' : ''}
          {/each}
        </div>
      {:else}
        <div class="flex flex-wrap items-center gap-3">
          <span class="font-semibold">{s.receptor.name}</span>
          <span class="mono text-xs text-muted">{s.receptor.id}</span>
          <span class="chip bg-surface-2 text-muted">{s.receptor.type}</span>
          <a href={`/receptors/${s.receptor.id}`} class="ml-auto text-xs text-accent hover:underline">Open receptor detail →</a>
        </div>
        <div class="mt-1 text-xs text-muted">{s.receptor.description}</div>
      {/if}
    </aside>
  {/if}
</div>
