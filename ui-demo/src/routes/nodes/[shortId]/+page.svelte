<script lang="ts">
  import { ArrowLeft } from 'lucide-svelte';
  import HealthDot from '$lib/components/HealthDot.svelte';
  import Sparkline, { type Bucket } from '$lib/components/Sparkline.svelte';
  import SignalRow from '$lib/components/SignalRow.svelte';
  import { signalsByNode, nodeHealth, now } from '$lib/stores/signals';
  import { healthLabel, relativeTime, severityRank } from '$lib/util';
  import type { SignalEvent } from '$lib/types';

  let { data } = $props();

  const events = $derived<SignalEvent[]>($signalsByNode[data.shortId] ?? []);
  const health = $derived($nodeHealth[data.shortId] ?? 'healthy');

  const counts = $derived.by(() => {
    const c = { info: 0, notice: 0, warning: 0, anomaly: 0, critical: 0 };
    for (const e of events) c[e.signal.severity] += 1;
    return c;
  });

  const clean = $derived(counts.info + counts.notice);
  const last = $derived(events[0]);

  // Bucket signals into 1-minute bins for the sparkline (last hour).
  const BUCKETS = 60;
  const BUCKET_MS = 60_000;
  const bins = $derived.by<Bucket[]>(() => {
    const end = $now;
    const start = end - BUCKETS * BUCKET_MS;
    const out: Bucket[] = Array.from({ length: BUCKETS }, () => ({ count: 0, maxSev: 0 }));
    for (const e of events) {
      const ts = new Date(e.signal.timestamp).getTime();
      if (ts < start || ts >= end) continue;
      const idx = Math.min(BUCKETS - 1, Math.floor((ts - start) / BUCKET_MS));
      out[idx].count += 1;
      const rank = severityRank(e.signal.severity);
      if (rank > out[idx].maxSev) out[idx].maxSev = rank;
    }
    return out;
  });
</script>

<div class="flex flex-col gap-4 p-6">
  <header class="card px-5 py-4">
    <div class="mb-1 flex items-center gap-2 text-xs text-muted">
      <a href="/nodes" class="inline-flex items-center gap-1 hover:text-accent"><ArrowLeft size={12} /> All nodes</a>
    </div>
    <div class="flex items-center gap-3">
      <h1 class="text-xl font-semibold">{data.shortId}</h1>
      <HealthDot {health} />
      <span
        class="text-xs font-semibold
        {health === 'healthy' ? 'text-sev-healthy' : ''}
        {health === 'warning' ? 'text-sev-warning' : ''}
        {health === 'anomaly' ? 'text-sev-anomaly' : ''}
        {health === 'critical' ? 'text-sev-critical' : ''}"
      >{healthLabel(health)}</span>
    </div>
    <div class="mt-1 mono text-[12px] text-muted">
      {data.node.type} · {data.node.uuid} · {data.node.layer} layer
    </div>
    <p class="mt-2 text-sm text-muted">{data.node.description}</p>
  </header>

  <section class="grid grid-cols-2 gap-4 md:grid-cols-5">
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Signals</div>
      <div class="mt-1 text-2xl font-semibold tabular-nums">{events.length}</div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Last signal</div>
      <div class="mt-1 text-sm">{last ? relativeTime(new Date(last.signal.timestamp).getTime(), $now) : '—'}</div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Critical</div>
      <div class="mt-1 text-2xl font-semibold tabular-nums text-sev-critical">{counts.critical}</div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Anomaly / Warning</div>
      <div class="mt-1 text-sm"><span class="text-sev-anomaly">{counts.anomaly}</span> · <span class="text-sev-warning">{counts.warning}</span></div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Clean</div>
      <div class="mt-1 text-2xl font-semibold tabular-nums text-muted">{clean}</div>
    </div>
  </section>

  <section class="card px-5 py-4">
    <div class="mb-2 flex items-center justify-between">
      <span class="text-sm font-medium">Signal activity · last hour</span>
      <span class="text-xs text-muted">1m buckets</span>
    </div>
    <Sparkline {bins} />
  </section>

  <section class="card px-5 py-4">
    <div class="mb-2 text-sm font-medium">Wired to</div>
    {#if data.wiredReceptors.length === 0}
      <div class="text-xs text-muted">No receptors are listening to this node.</div>
    {:else}
      <div class="flex flex-wrap gap-2">
        {#each data.wiredReceptors as r}
          <a href={`/receptors/${r.id}`} class="chip bg-surface-2 text-muted hover:text-accent">{r.id}</a>
        {/each}
      </div>
    {/if}
  </section>

  <section class="card">
    <div class="border-b border-border px-4 py-2 text-sm font-medium">Recent signals</div>
    <div class="max-h-[500px] overflow-y-auto">
      {#each events.slice(0, 100) as e (e.signal.signal_id)}
        <SignalRow event={e} now={$now} />
      {/each}
      {#if events.length === 0}
        <div class="p-6 text-center text-xs text-muted">No signals yet.</div>
      {/if}
    </div>
  </section>
</div>
