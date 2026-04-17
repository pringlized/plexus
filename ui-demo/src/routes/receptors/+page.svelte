<script lang="ts">
  import { receptors, receiptsByReceptor, sim } from '$lib/sim/store.svelte';
  import { relativeTime } from '$lib/util';
  import { Radar } from 'lucide-svelte';
</script>

<div class="flex flex-col gap-4 p-6">
  <header>
    <h1 class="text-lg font-semibold tracking-wide">Receptors</h1>
    <p class="text-sm text-muted">Subscribers that decide what to do when a matching signal arrives.</p>
  </header>
  <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
    {#each receptors as r}
      {@const last = receiptsByReceptor(r.id, 1)[0]}
      <a href={`/receptors/${r.id}`} class="card flex flex-col gap-2 px-4 py-3 text-sm transition hover:border-accent/60">
        <div class="flex items-center gap-2">
          <Radar size={14} class="text-accent" />
          <span class="truncate font-semibold">{r.name}</span>
          <span class="ml-auto inline-flex h-2 w-2 rounded-full bg-sev-healthy"></span>
        </div>
        <div class="mono text-[11px] text-muted">{r.type} · {r.id}</div>
        <div class="text-xs text-muted">{r.description}</div>
        <div class="mono text-[11px] text-muted">
          Listens: {r.listensTo === '*' ? 'all nodes' : r.listensTo.join(', ')} · Fires on: {r.firesOn === '*' ? 'all' : r.firesOn.join(',')}
        </div>
        {#if last}
          <div class="mono text-[11px] text-muted">Last: {last.summary} · {relativeTime(last.timestamp, sim.now)}</div>
        {/if}
      </a>
    {/each}
  </div>
</div>
