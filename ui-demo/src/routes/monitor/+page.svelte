<script lang="ts">
  import { onMount } from 'svelte';
  import { Pause, Play, Zap, CheckCircle2, Loader2 } from 'lucide-svelte';
  import SeverityBadge from '$lib/components/SeverityBadge.svelte';
  import SignalRow from '$lib/components/SignalRow.svelte';
  import {
    sim,
    receptors,
    nodes,
    togglePause
  } from '$lib/sim/store.svelte';
  import { LAYERS } from '$lib/sim/fixtures';
  import type { LayerId, Severity } from '$lib/sim/types';
  import { relativeTime } from '$lib/util';

  let layerFilter: LayerId | 'all' = $state('all');
  let severityFilter: Severity | 'all' = $state('all');
  let nodeFilter: string = $state('all');

  onMount(() => {
    const p = new URLSearchParams(window.location.search).get('layer');
    if (p === 'security' || p === 'ingestion' || p === 'build') layerFilter = p;
  });

  const filteredSignals = $derived(
    sim.signals.filter((s) => {
      if (layerFilter !== 'all' && s.system_layer !== layerFilter) return false;
      if (severityFilter !== 'all' && s.severity !== severityFilter) return false;
      if (nodeFilter !== 'all' && s.node_id !== nodeFilter) return false;
      return true;
    }).slice(0, 120)
  );
  const visibleSignalIds = $derived(new Set(filteredSignals.map((s) => s.signal_id)));
  const receipts = $derived(sim.receipts.filter((r) => visibleSignalIds.has(r.signal_id)).slice(0, 120));
  const actions = $derived(sim.actions.filter((a) => visibleSignalIds.has(a.signal_id)).slice(0, 60));

  function nodeName(id: string) {
    return nodes.find((n) => n.id === id)?.name ?? id;
  }
  function receptorName(id: string) {
    return receptors.find((r) => r.id === id)?.name ?? id;
  }
</script>

<div class="flex h-full flex-col p-6 pb-0">
  <header class="mb-4 flex flex-wrap items-center gap-3">
    <div>
      <h1 class="text-lg font-semibold tracking-wide">Live Signal Monitor</h1>
      <p class="text-sm text-muted">Node broadcasts → receptor receipts → receptor actions.</p>
    </div>
    <div class="ml-auto flex flex-wrap items-center gap-2">
      <select bind:value={layerFilter} class="rounded-md border border-border bg-surface px-2 py-1 text-xs">
        <option value="all">All layers</option>
        {#each LAYERS as l}
          <option value={l.id}>{l.name}</option>
        {/each}
      </select>
      <select bind:value={severityFilter} class="rounded-md border border-border bg-surface px-2 py-1 text-xs">
        <option value="all">All severities</option>
        <option value="info">info</option>
        <option value="notice">notice</option>
        <option value="warning">warning</option>
        <option value="anomaly">anomaly</option>
        <option value="critical">critical</option>
      </select>
      <select bind:value={nodeFilter} class="rounded-md border border-border bg-surface px-2 py-1 text-xs">
        <option value="all">All nodes</option>
        {#each nodes as n}
          <option value={n.id}>{n.name}</option>
        {/each}
      </select>
      <button
        type="button"
        onclick={togglePause}
        class="inline-flex items-center gap-1 rounded border border-border bg-surface px-2 py-1 text-xs text-muted transition hover:text-text"
      >
        {#if sim.paused}
          <Play size={12}/> Resume
          {#if sim.queuedWhilePaused > 0}<span class="rounded bg-sev-critical/20 px-1.5 text-sev-critical">{sim.queuedWhilePaused}</span>{/if}
        {:else}
          <Pause size={12}/> Pause
        {/if}
      </button>
    </div>
  </header>

  <div class="grid min-h-0 flex-1 grid-cols-3 gap-4 pb-6">
    <!-- Node broadcasts -->
    <section class="card flex min-h-0 flex-col">
      <div class="flex items-center justify-between border-b border-border px-3 py-2">
        <span class="text-xs font-semibold uppercase tracking-wider text-muted">Node Broadcasts</span>
        <span class="text-[10px] text-muted">{filteredSignals.length}</span>
      </div>
      <div class="min-h-0 flex-1 overflow-y-auto">
        {#each filteredSignals as s (s.signal_id)}
          <div class="animate-slide-in"><SignalRow signal={s} /></div>
        {/each}
      </div>
    </section>

    <!-- Receptor receipts -->
    <section class="card flex min-h-0 flex-col">
      <div class="flex items-center justify-between border-b border-border px-3 py-2">
        <span class="text-xs font-semibold uppercase tracking-wider text-muted">Receptor Receipts</span>
        <span class="text-[10px] text-muted">{receipts.length}</span>
      </div>
      <div class="min-h-0 flex-1 overflow-y-auto">
        {#each receipts as r (r.id)}
          <div class="animate-slide-in border-b border-border/60 px-3 py-2 text-sm">
            <div class="flex items-center gap-2">
              <SeverityBadge severity={r.severity} size="sm" />
              <span class="text-xs text-muted">{relativeTime(r.timestamp, sim.now)}</span>
              <a href={`/receptors/${r.receptor_id}`} class="truncate font-medium hover:text-accent">
                {receptorName(r.receptor_id)}
              </a>
              <span class="ml-auto text-[11px] text-sev-healthy">✓</span>
            </div>
            <div class="mt-0.5 mono text-[11px] text-muted">
              ← {nodeName(r.node_id)} · {r.summary}
            </div>
          </div>
        {/each}
        {#if receipts.length === 0}
          <div class="p-6 text-center text-xs text-muted">No receipts match filters.</div>
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
        {#each actions as a (a.id)}
          <div class="animate-slide-in border-b border-border/60 px-3 py-2 text-sm">
            <div class="flex items-center gap-2">
              <Zap size={13} class="text-accent" />
              <a href={`/receptors/${a.receptor_id}`} class="truncate font-medium hover:text-accent">
                {receptorName(a.receptor_id)}
              </a>
              <span class="text-xs text-muted">{relativeTime(a.timestamp, sim.now)}</span>
              <span class="ml-auto">
                {#if a.status === 'pending'}
                  <Loader2 size={12} class="animate-spin text-muted" />
                {:else if a.status === 'completed'}
                  <CheckCircle2 size={12} class="text-sev-healthy" />
                {/if}
              </span>
            </div>
            <div class="mt-0.5 text-[12px]">{a.action}</div>
            <div class="mono mt-0.5 text-[11px] text-muted">{a.detail}</div>
            {#if a.duration_ms !== undefined}
              <div class="mono mt-0.5 text-[10px] text-muted">↳ {a.duration_ms}ms</div>
            {/if}
          </div>
        {/each}
        {#if actions.length === 0}
          <div class="p-6 text-center text-xs text-muted">No meaningful actions yet. Wait for the critical cascade.</div>
        {/if}
      </div>
    </section>
  </div>
</div>
