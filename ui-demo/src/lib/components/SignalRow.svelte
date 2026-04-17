<script lang="ts">
  import { ChevronRight, Zap } from 'lucide-svelte';
  import SeverityBadge from './SeverityBadge.svelte';
  import { basename, relativeTime, shortHash } from '$lib/util';
  import type { SignalEvent } from '$lib/types';

  let {
    event,
    now: nowMs,
    compact = false
  }: { event: SignalEvent; now: number; compact?: boolean } = $props();

  let expanded = $state(false);
  const ts = $derived(new Date(event.timestamp).getTime());
</script>

<div
  class="group flex flex-col gap-1 border-b border-border/60 px-3 py-2 text-sm transition hover:bg-surface-2
    {event.severity === 'critical' ? 'animate-flash' : ''}"
>
  <div class="flex items-center gap-2">
    <SeverityBadge
      severity={event.severity}
      pulse={event.severity !== 'info' && event.severity !== 'notice'}
    />
    <span class="text-xs text-muted">{relativeTime(ts, nowMs)}</span>
    <a
      href={`/nodes/${event.pinch_id}`}
      class="truncate font-medium hover:text-accent"
      onclick={(e) => e.stopPropagation()}
    >
      {event.name ?? shortHash(event.pinch_id)}
    </a>
    <span class="mono truncate text-muted">{event.source_function}</span>
    {#if event.action}
      <span class="chip bg-accent/15 text-accent text-[10px]">
        <Zap size={9} class="inline" />
        {event.action}
      </span>
    {/if}
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
  <div class="mono pl-0.5 text-[10.5px] text-muted/80">
    ↳ {basename(event.source_file)}:{event.source_line}
  </div>
  {#if expanded && !compact}
    <pre class="mono overflow-x-auto rounded border border-border bg-bg px-3 py-2 text-[11px] text-text/80">{JSON.stringify(event.payload, null, 2)}</pre>
    {#if event.action_result}
      <div class="mono text-[10.5px] text-muted/80">
        {event.action_result.batch ? `batch: ${event.action_result.batch}` : 'single action'}
        · fired: {event.action_result.actions_fired.join(', ')}
        · {event.action_result.ok ? 'ok' : 'FAILED'}
      </div>
    {/if}
  {/if}
</div>
