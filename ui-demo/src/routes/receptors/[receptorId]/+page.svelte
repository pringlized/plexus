<script lang="ts">
  import { ArrowLeft, Zap, CheckCircle2 } from 'lucide-svelte';
  import SeverityBadge from '$lib/components/SeverityBadge.svelte';
  import { signalsByReceptor, now } from '$lib/stores/signals';
  import { relativeTime } from '$lib/util';
  import type { SignalEvent, ReceptorResultData } from '$lib/types';

  let { data } = $props();

  const events = $derived<SignalEvent[]>($signalsByReceptor[data.receptorId] ?? []);

  type ReceptorHit = { event: SignalEvent; result: ReceptorResultData };
  const hits = $derived<ReceptorHit[]>(
    events
      .map((e) => ({
        event: e,
        result: e.receptor_results.find((r) => r.receptor_id === data.receptorId)
      }))
      .filter((h): h is ReceptorHit => h.result !== undefined)
  );

  const flagged = $derived(hits.filter((h) => h.result.action !== 'discard'));
  const receiptCount = $derived(hits.length);
  const invocationCount = $derived(flagged.length);
  const successful = $derived(invocationCount); // all flags are successful in rev1
</script>

<div class="flex flex-col gap-4 p-6">
  <header class="card px-5 py-4">
    <div class="mb-1 flex items-center gap-2 text-xs text-muted">
      <a href="/receptors" class="inline-flex items-center gap-1 hover:text-accent"><ArrowLeft size={12} /> All receptors</a>
    </div>
    <div class="flex items-center gap-3">
      <h1 class="text-xl font-semibold">{data.receptorId}</h1>
      <span class="chip bg-sev-healthy/15 text-sev-healthy">ACTIVE</span>
    </div>
    <div class="mt-1 mono text-[12px] text-muted">{data.receptor.type} · {data.receptor.uuid}</div>
    <p class="mt-2 text-sm text-muted">{data.receptor.description}</p>
  </header>

  <section class="card px-5 py-4">
    <div class="mb-2 text-sm font-medium">Configuration</div>
    <div class="grid grid-cols-1 gap-3 text-sm md:grid-cols-3">
      <div>
        <span class="text-muted">Listens to:</span>
        <div class="mt-1 flex flex-wrap gap-1">
          {#each data.listenedNodes as n}
            <a href={`/nodes/${n.id}`} class="chip bg-surface-2 text-muted hover:text-accent">{n.id}</a>
          {/each}
        </div>
      </div>
      <div>
        <span class="text-muted">Fires on:</span>
        <div class="mt-1 mono text-xs">
          {data.receptor.config.severity_filter?.join(', ') ?? '—'}
        </div>
      </div>
      <div>
        <span class="text-muted">Action:</span>
        <div class="mt-1 mono text-xs">{data.receptor.config.alert_label ?? data.receptor.type}</div>
      </div>
    </div>
  </section>

  <section class="grid grid-cols-2 gap-4 md:grid-cols-4">
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Invocations</div>
      <div class="mt-1 text-2xl font-semibold tabular-nums">{invocationCount}</div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Successful</div>
      <div class="mt-1 text-2xl font-semibold tabular-nums text-sev-healthy">{successful}</div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Receipts</div>
      <div class="mt-1 text-2xl font-semibold tabular-nums">{receiptCount}</div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Discard rate</div>
      <div class="mt-1 text-sm">{receiptCount ? Math.round(((receiptCount - invocationCount) / receiptCount) * 100) : 0}%</div>
    </div>
  </section>

  <section class="card">
    <div class="border-b border-border px-4 py-2 text-sm font-medium">Recent actions</div>
    <div class="max-h-[420px] overflow-y-auto">
      {#each flagged.slice(0, 60) as h (h.event.signal.signal_id)}
        <div class="border-b border-border/60 px-4 py-2.5 text-sm">
          <div class="flex items-center gap-2">
            <Zap size={13} class="text-accent" />
            <span class="font-medium">Flagged</span>
            <span class="text-xs text-muted">{relativeTime(new Date(h.event.signal.timestamp).getTime(), $now)}</span>
            <span class="ml-auto"><CheckCircle2 size={12} class="text-sev-healthy" /></span>
          </div>
          <div class="mono mt-1 text-[11px] text-muted">{h.result.flag_reason}</div>
          <div class="mono mt-0.5 text-[10px] text-muted">
            Node:
            <a href={`/nodes/${h.event.signal.node_short_id}`} class="hover:text-accent">{h.event.signal.node_short_id}</a>
            · {h.event.signal.category}
          </div>
        </div>
      {/each}
      {#if flagged.length === 0}
        <div class="p-6 text-center text-xs text-muted">No actions yet.</div>
      {/if}
    </div>
  </section>

  <section class="card">
    <div class="border-b border-border px-4 py-2 text-sm font-medium">Recent receipts</div>
    <div class="max-h-[420px] overflow-y-auto">
      {#each hits.slice(0, 80) as h (h.event.signal.signal_id)}
        <div class="border-b border-border/60 px-4 py-2 text-sm">
          <div class="flex items-center gap-2">
            <SeverityBadge severity={h.event.signal.severity} size="sm" />
            <span class="text-xs text-muted">{relativeTime(new Date(h.event.signal.timestamp).getTime(), $now)}</span>
            <span>from <a href={`/nodes/${h.event.signal.node_short_id}`} class="hover:text-accent">{h.event.signal.node_short_id}</a></span>
            <span class="ml-auto text-[11px] {h.result.action === 'discard' ? 'text-muted' : 'text-sev-healthy'}">
              {h.result.action === 'discard' ? '/dev/null' : '✓'}
            </span>
          </div>
          <div class="mono mt-0.5 text-[11px] text-muted">{h.result.flag_reason ?? h.event.signal.category}</div>
        </div>
      {/each}
      {#if hits.length === 0}
        <div class="p-6 text-center text-xs text-muted">No receipts yet.</div>
      {/if}
    </div>
  </section>
</div>
