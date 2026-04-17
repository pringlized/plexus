<script lang="ts">
  import { nodes, signalsByNode, nodeHealth, sim } from '$lib/sim/store.svelte';
  import HealthDot from '$lib/components/HealthDot.svelte';
  import { relativeTime } from '$lib/util';
  import { Cpu } from 'lucide-svelte';
</script>

<div class="flex flex-col gap-4 p-6">
  <header>
    <h1 class="text-lg font-semibold tracking-wide">Nodes</h1>
    <p class="text-sm text-muted">Registered signal emitters — click to open detail.</p>
  </header>
  <div class="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
    {#each nodes as n}
      {@const recent = signalsByNode(n.id, 1)[0]}
      {@const h = nodeHealth(n.id)}
      <a href={`/nodes/${n.id}`} class="card flex flex-col gap-2 px-4 py-3 text-sm transition hover:border-accent/60">
        <div class="flex items-center gap-2">
          <Cpu size={14} class="text-muted" />
          <span class="truncate font-semibold">{n.name}</span>
          <HealthDot health={h} />
        </div>
        <div class="mono text-[11px] text-muted">{n.type} · {n.id} · {n.layer} layer</div>
        <div class="text-xs text-muted">{n.description}</div>
        {#if recent}
          <div class="mono mt-1 text-[11px] text-muted">Last: {recent.category} · {relativeTime(recent.timestamp, sim.now)}</div>
        {/if}
      </a>
    {/each}
  </div>
</div>
