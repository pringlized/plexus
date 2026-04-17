<script lang="ts">
  import { page } from '$app/stores';
  import { CheckCircle2, Zap } from 'lucide-svelte';
  import SeverityBadge from '$lib/components/SeverityBadge.svelte';
  import SignalRow from '$lib/components/SignalRow.svelte';
  import { deriveLayers } from '$lib/config-helpers';
  import { signalEvents, now } from '$lib/stores/signals';
  import { relativeTime } from '$lib/util';

  let { data } = $props();

  const layers = $derived(deriveLayers(data.nodes));
  const nodeCount = $derived(Object.keys(data.nodes).length);
  const receptorCount = $derived(Object.keys(data.receptors).length);

  const activeLayerName = $derived($page.url.searchParams.get('layer'));
  const activeLayer = $derived(
    activeLayerName ? layers.find((l) => l.name === activeLayerName) ?? null : null
  );

  // Apply layer filter (if any) to broadcasts.
  const broadcasts = $derived(
    ($signalEvents ?? []).filter(
      (e) => !activeLayerName || e.signal.node_layer === activeLayerName
    )
  );

  // Receipts: one row per (event, receptor_result). Discarded signals still
  // produce receipts because the receptor saw them.
  type Receipt = {
    id: string;
    receptor_id: string;
    severity: string;
    action: string;
    flag_reason: string | null;
    node_short_id: string;
    timestamp: number;
  };
  type Action = Receipt & { flag_reason: string };

  const receipts = $derived<Receipt[]>(
    broadcasts.flatMap((e) =>
      e.receptor_results.map((r) => ({
        id: `${e.signal.signal_id}::${r.receptor_id}`,
        receptor_id: r.receptor_id,
        severity: e.signal.severity,
        action: r.action,
        flag_reason: r.flag_reason,
        node_short_id: e.signal.node_short_id,
        timestamp: new Date(e.signal.timestamp).getTime()
      }))
    )
  );

  // Actions: only flag/flag+action receipts (with a reason).
  const actions = $derived<Action[]>(
    receipts.filter(
      (r): r is Action =>
        (r.action === 'flag' || r.action === 'flag+action') && r.flag_reason !== null
    )
  );
</script>

<div class="flex h-full flex-col p-6 pb-0">
  <header class="mb-4 flex flex-wrap items-center gap-3">
    <div>
      <h1 class="text-lg font-semibold tracking-wide">Live Signal Monitor</h1>
      <p class="text-sm text-muted">Node broadcasts → receptor receipts → receptor actions.</p>
    </div>
    <div class="ml-auto flex items-center gap-3 text-xs text-muted">
      <span>{nodeCount} nodes</span>
      <span>·</span>
      <span>{receptorCount} receptors</span>
      <span>·</span>
      <span>{layers.length} layers</span>
    </div>
  </header>

  {#if activeLayer}
    <div class="mb-4 border-l-2 border-accent/60 pl-3">
      <h2 class="text-base font-semibold capitalize">{activeLayer.name} Layer</h2>
      <p class="text-sm text-muted">{activeLayer.description}</p>
    </div>
  {:else if activeLayerName}
    <div class="mb-4 border-l-2 border-sev-warning/60 pl-3">
      <h2 class="text-base font-semibold capitalize">{activeLayerName} Layer</h2>
      <p class="text-sm text-muted">No nodes currently configured in this layer.</p>
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
        {#each broadcasts.slice(0, 120) as e (e.signal.signal_id)}
          <div class="animate-slide-in"><SignalRow event={e} now={$now} compact /></div>
        {/each}
        {#if broadcasts.length === 0}
          <div class="flex h-full items-center justify-center p-6 text-center text-xs text-muted">
            Waiting for signals…
          </div>
        {/if}
      </div>
    </section>

    <!-- Receptor receipts -->
    <section class="card flex min-h-0 flex-col">
      <div class="flex items-center justify-between border-b border-border px-3 py-2">
        <span class="text-xs font-semibold uppercase tracking-wider text-muted">Receptor Receipts</span>
        <span class="text-[10px] text-muted">{receipts.length}</span>
      </div>
      <div class="min-h-0 flex-1 overflow-y-auto">
        {#each receipts.slice(0, 120) as r (r.id)}
          <div class="animate-slide-in border-b border-border/60 px-3 py-2 text-sm">
            <div class="flex items-center gap-2">
              <SeverityBadge severity={r.severity} size="sm" />
              <span class="text-xs text-muted">{relativeTime(r.timestamp, $now)}</span>
              <a href={`/receptors/${r.receptor_id}`} class="truncate font-medium hover:text-accent">
                {r.receptor_id}
              </a>
              <span class="ml-auto text-[11px] {r.action === 'discard' ? 'text-muted' : 'text-sev-healthy'}">
                {r.action === 'discard' ? '/dev/null' : '✓'}
              </span>
            </div>
            <div class="mt-0.5 mono text-[11px] text-muted">
              ← {r.node_short_id}{r.flag_reason ? ` · ${r.flag_reason}` : ''}
            </div>
          </div>
        {/each}
        {#if receipts.length === 0}
          <div class="flex h-full items-center justify-center p-6 text-center text-xs text-muted">
            Receipts will appear here as receptors react to signals.
          </div>
        {/if}
      </div>
    </section>

    <!-- Receptor actions -->
    <section class="card flex min-h-0 flex-col">
      <div class="flex items-center justify-between border-b border-border px-3 py-2">
        <span class="text-xs font-semibold uppercase tracking-wider text-muted">Receptor Actions</span>
        <span class="text-[10px] text-muted">{actions.length}</span>
      </div>
      <div class="min-h-0 flex-1 overflow-y-auto">
        {#each actions.slice(0, 60) as a (a.id)}
          <div class="animate-slide-in border-b border-border/60 px-3 py-2 text-sm">
            <div class="flex items-center gap-2">
              <Zap size={13} class="text-accent" />
              <a href={`/receptors/${a.receptor_id}`} class="truncate font-medium hover:text-accent">
                {a.receptor_id}
              </a>
              <span class="text-xs text-muted">{relativeTime(a.timestamp, $now)}</span>
              <span class="ml-auto"><CheckCircle2 size={12} class="text-sev-healthy" /></span>
            </div>
            <div class="mono mt-0.5 text-[11px] text-muted">{a.flag_reason}</div>
          </div>
        {/each}
        {#if actions.length === 0}
          <div class="flex h-full items-center justify-center p-6 text-center text-xs text-muted">
            No actions yet.
          </div>
        {/if}
      </div>
    </section>
  </div>
</div>
