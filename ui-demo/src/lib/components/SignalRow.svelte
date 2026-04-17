<script lang="ts">
  import SeverityBadge from './SeverityBadge.svelte';
  import { relativeTime } from '$lib/util';
  import type { SignalEvent } from '$lib/types';
  import { ChevronRight } from 'lucide-svelte';

  let {
    event,
    now = Date.now(),
    compact = false
  }: { event: SignalEvent; now?: number; compact?: boolean } = $props();

  let expanded = $state(false);

  const signal = $derived(event.signal);
  const ts = $derived(new Date(signal.timestamp).getTime());
  const filename = $derived(signal.source_file ? signal.source_file.split('/').pop() : null);
  const location = $derived(
    filename && signal.source_line ? `${filename}:${signal.source_line}` : null
  );
</script>

<div
  class="group flex flex-col gap-1 border-b border-border/60 px-3 py-2 text-sm transition hover:bg-surface-2
    {signal.severity === 'critical' ? 'animate-flash' : ''}"
>
  <div class="flex items-center gap-2">
    <SeverityBadge
      severity={signal.severity}
      pulse={signal.severity !== 'info' && signal.severity !== 'notice'}
    />
    <span class="text-xs text-muted">{relativeTime(ts, now)}</span>
    <a
      href={`/nodes/${signal.node_short_id}`}
      class="truncate font-medium hover:text-accent"
      onclick={(e) => e.stopPropagation()}
    >
      {signal.node_short_id}
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
  {#if location}
    <div class="mono pl-0.5 text-[10.5px] text-muted/80">↳ {location}</div>
  {/if}
  {#if expanded && !compact}
    <pre class="mono overflow-x-auto rounded border border-border bg-bg px-3 py-2 text-[11px] text-text/80">{JSON.stringify(signal.payload, null, 2)}</pre>
  {/if}
</div>
