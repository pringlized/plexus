<script lang="ts">
  import { page } from '$app/stores';
  import { CheckCircle2, X, Zap } from 'lucide-svelte';
  import SeverityBadge from '$lib/components/SeverityBadge.svelte';
  import SignalRow from '$lib/components/SignalRow.svelte';
  import { signalEvents, actionEvents, now, nodesByLayer } from '$lib/stores/signals';
  import { basename, relativeTime, shortHash } from '$lib/util';

  let { data } = $props();

  const activeLayer = $derived($page.url.searchParams.get('layer'));

  const broadcasts = $derived(
    activeLayer
      ? $signalEvents.filter((e) => (e.layer ?? 'Undefined') === activeLayer)
      : $signalEvents
  );
  const visibleIds = $derived(new Set(broadcasts.map((e) => e.pinch_id + e.received_at)));
  const receipts = $derived(
    $actionEvents.filter((e) => visibleIds.has(e.pinch_id + e.received_at))
  );

  const layerNodes = $derived(activeLayer ? $nodesByLayer.get(activeLayer) ?? [] : []);
</script>

<div class="flex h-full flex-col p-6 pb-0">
  <header class="mb-4 flex flex-wrap items-center gap-3">
    <div>
      <h1 class="text-lg font-semibold tracking-wide">Live Signal Monitor</h1>
      <p class="text-sm text-muted">Node broadcasts → action receipts → action results.</p>
    </div>
    <div class="ml-auto flex items-center gap-3 text-xs text-muted">
      <span>{$signalEvents.length} signals</span>
      <span>·</span>
      <span>{data.actions.length} actions</span>
      <span>·</span>
      <span>{data.batches.length} batches</span>
    </div>
  </header>

  {#if activeLayer}
    <div class="mb-4 border-l-2 border-accent/60 pl-3">
      <h2 class="text-base font-semibold capitalize">{activeLayer} Layer</h2>
      <p class="text-sm text-muted">
        {layerNodes.length === 0
          ? 'No nodes have emitted from this layer yet.'
          : `${layerNodes.length} ${layerNodes.length === 1 ? 'node' : 'nodes'} emitting.`}
      </p>
    </div>
  {/if}

  <div class="grid min-h-0 flex-1 grid-cols-3 gap-4 pb-6">
    <!-- Node broadcasts -->
    <section class="card flex min-h-0 flex-col">
      <div class="flex items-center justify-between border-b border-border px-3 py-2">
        <span class="text-xs font-semibold uppercase tracking-wider text-muted">Node Broadcasts</span>
        <span class="text-[10px] text-muted">{broadcasts.length}</span>
      </div>
      <div class="min-h-0 flex-1 overflow-y-auto">
        {#each broadcasts.slice(0, 200) as e (e.pinch_id + '-' + e.received_at)}
          <div class="animate-slide-in"><SignalRow event={e} now={$now} compact /></div>
        {/each}
        {#if broadcasts.length === 0}
          <div class="flex h-full items-center justify-center p-6 text-center text-xs text-muted">
            Waiting for signals…
          </div>
        {/if}
      </div>
    </section>

    <!-- Action receipts -->
    <section class="card flex min-h-0 flex-col">
      <div class="flex items-center justify-between border-b border-border px-3 py-2">
        <span class="text-xs font-semibold uppercase tracking-wider text-muted">Action Receipts</span>
        <span class="text-[10px] text-muted">{receipts.length}</span>
      </div>
      <div class="min-h-0 flex-1 overflow-y-auto">
        {#each receipts.slice(0, 120) as e (e.pinch_id + '-' + e.received_at + '-rcpt')}
          <div class="animate-slide-in border-b border-border/60 px-3 py-2 text-sm">
            <div class="flex items-center gap-2">
              <SeverityBadge severity={e.severity} size="sm" />
              <span class="text-xs text-muted">{relativeTime(e.received_at, $now)}</span>
              <a href={`/actions/${e.action}`} class="truncate font-medium hover:text-accent">
                {e.action}
              </a>
            </div>
            <div class="mono mt-0.5 text-[11px] text-muted">
              ← {e.name ?? shortHash(e.pinch_id)} · {basename(e.source_file)}:{e.source_line}
            </div>
          </div>
        {/each}
        {#if receipts.length === 0}
          <div class="flex h-full items-center justify-center p-6 text-center text-xs text-muted">
            Receipts appear as actions or batches fire.
          </div>
        {/if}
      </div>
    </section>

    <!-- Action results -->
    <section class="card flex min-h-0 flex-col">
      <div class="flex items-center justify-between border-b border-border px-3 py-2">
        <span class="text-xs font-semibold uppercase tracking-wider text-muted">Action Results</span>
        <span class="text-[10px] text-muted">{receipts.length}</span>
      </div>
      <div class="min-h-0 flex-1 overflow-y-auto">
        {#each receipts.slice(0, 120) as e (e.pinch_id + '-' + e.received_at + '-res')}
          {#if e.action_result}
            <div class="animate-slide-in border-b border-border/60 px-3 py-2 text-sm">
              <div class="flex items-center gap-2">
                <Zap size={13} class="text-accent" />
                <span class="font-medium">
                  {e.action_result.batch ?? 'single'}
                </span>
                <span class="text-xs text-muted">{relativeTime(e.received_at, $now)}</span>
                <span class="ml-auto">
                  {#if e.action_result.ok}
                    <CheckCircle2 size={12} class="text-sev-healthy" />
                  {:else}
                    <X size={12} class="text-sev-critical" />
                  {/if}
                </span>
              </div>
              <div class="mono mt-0.5 text-[11px] text-muted">
                fired: {e.action_result.actions_fired.join(', ')}
              </div>
              {#if e.action_result.detail}
                <div class="mono mt-0.5 text-[10px] text-sev-critical/80">
                  {e.action_result.detail}
                </div>
              {/if}
            </div>
          {/if}
        {/each}
        {#if receipts.length === 0}
          <div class="flex h-full items-center justify-center p-6 text-center text-xs text-muted">
            No results yet.
          </div>
        {/if}
      </div>
    </section>
  </div>
</div>
