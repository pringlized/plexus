<script lang="ts">
  import SeverityBadge from './SeverityBadge.svelte';
  import { sim, nodes } from '$lib/sim/store.svelte';
  import { relativeTime } from '$lib/util';
  import type { Signal } from '$lib/sim/types';
  import { ChevronRight } from 'lucide-svelte';

  let { signal, compact = false }: { signal: Signal; compact?: boolean } = $props();

  let expanded = $state(false);
  const node = $derived(nodes.find((n) => n.id === signal.node_id));
</script>

<div
  class="group flex flex-col gap-1 border-b border-border/60 px-3 py-2 text-sm transition hover:bg-surface-2
    {signal.severity === 'critical' ? 'animate-flash' : ''}"
>
  <div class="flex items-center gap-2">
    <SeverityBadge severity={signal.severity} pulse={signal.severity !== 'info' && signal.severity !== 'notice'} />
    <span class="text-xs text-muted">{relativeTime(signal.timestamp, sim.now)}</span>
    <a
      href={`/nodes/${signal.node_id}`}
      class="truncate font-medium hover:text-accent"
      onclick={(e) => e.stopPropagation()}
    >
      {node?.name ?? signal.node_id}
    </a>
    <span class="mono truncate text-muted">{signal.category}</span>
    {#if !compact}
      <button
        type="button"
        class="ml-auto inline-flex items-center gap-0.5 text-muted opacity-0 transition group-hover:opacity-100"
        onclick={() => (expanded = !expanded)}
      >
        <ChevronRight size={14} class={expanded ? 'rotate-90' : ''} />
      </button>
    {/if}
  </div>
  {#if expanded && !compact}
    <pre class="mono overflow-x-auto rounded border border-border bg-bg px-3 py-2 text-[11px] text-text/80">{JSON.stringify(signal.payload, null, 2)}</pre>
  {/if}
</div>
