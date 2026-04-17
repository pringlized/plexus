<script lang="ts">
  import HealthDot from '$lib/components/HealthDot.svelte';
  import { Cpu } from 'lucide-svelte';

  let { data } = $props();
</script>

<div class="flex flex-col gap-4 p-6">
  <header>
    <h1 class="text-lg font-semibold tracking-wide">Nodes</h1>
    <p class="text-sm text-muted">Registered signal emitters from <code class="mono">plexus-nodes.yaml</code> — click to open detail.</p>
  </header>
  <div class="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
    {#each Object.entries(data.nodes) as [shortId, node]}
      <a href={`/nodes/${shortId}`} class="card flex flex-col gap-2 px-4 py-3 text-sm transition hover:border-accent/60">
        <div class="flex items-center gap-2">
          <Cpu size={14} class="text-muted" />
          <span class="truncate font-semibold">{shortId}</span>
          <HealthDot health="healthy" pulse={false} />
        </div>
        <div class="mono text-[11px] text-muted">{node.type} · {node.layer} layer</div>
        <div class="text-xs text-muted">{node.description}</div>
        <div class="mono text-[10px] text-muted">{node.uuid}</div>
      </a>
    {/each}
  </div>
</div>
