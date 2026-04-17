<script lang="ts">
  import { Radar } from 'lucide-svelte';
  import { signalsByReceptor, now } from '$lib/stores/signals';
  import { relativeTime } from '$lib/util';

  let { data } = $props();
</script>

<div class="flex flex-col gap-4 p-6">
  <header>
    <h1 class="text-lg font-semibold tracking-wide">Receptors</h1>
    <p class="text-sm text-muted">Subscribers from <code class="mono">plexus-receptors.yaml</code> that decide what to do when a matching signal arrives.</p>
  </header>
  <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
    {#each Object.entries(data.receptors) as [receptorId, receptor]}
      {@const last = ($signalsByReceptor[receptorId] ?? [])[0]}
      <a href={`/receptors/${receptorId}`} class="card flex flex-col gap-2 px-4 py-3 text-sm transition hover:border-accent/60">
        <div class="flex items-center gap-2">
          <Radar size={14} class="text-accent" />
          <span class="truncate font-semibold">{receptorId}</span>
          <span class="ml-auto inline-flex h-2 w-2 rounded-full bg-sev-healthy"></span>
        </div>
        <div class="mono text-[11px] text-muted">{receptor.type}</div>
        <div class="text-xs text-muted">{receptor.description}</div>
        <div class="mono text-[11px] text-muted">
          Listens: {receptor.listens_to.join(', ')}
          {#if receptor.config.severity_filter}
            · Fires on: {receptor.config.severity_filter.join(', ')}
          {/if}
        </div>
        {#if last}
          <div class="mono text-[11px] text-muted">
            Last: {last.signal.severity} · {relativeTime(new Date(last.signal.timestamp).getTime(), $now)}
          </div>
        {/if}
      </a>
    {/each}
  </div>
</div>
