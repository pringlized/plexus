<script lang="ts">
  import { ArrowLeft } from 'lucide-svelte';
  import { page } from '$app/stores';
  import HealthDot from '$lib/components/HealthDot.svelte';
  import SignalRow from '$lib/components/SignalRow.svelte';
  import { nodeRegistry, signalsForNode, now } from '$lib/stores/signals';
  import { basename, relativeTime, statusLabel } from '$lib/util';

  const pinchId = $derived($page.params.pinch_id);
  const node = $derived($nodeRegistry.get(pinchId));
  const signals = $derived(signalsForNode(pinchId));

  const counts = $derived.by(() => {
    const c = { info: 0, notice: 0, warning: 0, anomaly: 0, critical: 0 };
    for (const e of $signals) c[e.severity] += 1;
    return c;
  });
  const clean = $derived(counts.info + counts.notice);
  const status = $derived(node?.last_severity ?? 'healthy');
</script>

{#if !node}
  <div class="flex min-h-[200px] flex-col items-center justify-center gap-3 p-6 text-sm text-muted">
    <p>No signals from this pinch yet.</p>
    <a href="/" class="text-xs text-accent hover:underline">← Back to Dashboard</a>
  </div>
{:else}
  <div class="flex flex-col gap-4 p-6">
    <header class="card px-5 py-4">
      <div class="mb-1 flex items-center gap-2 text-xs text-muted">
        <a href="/" class="inline-flex items-center gap-1 hover:text-accent"><ArrowLeft size={12} /> Dashboard</a>
      </div>
      <div class="flex items-center gap-3">
        <h1 class="text-xl font-semibold">{node.name ?? node.pinch_id.slice(0, 8)}</h1>
        <HealthDot {status} />
        <span
          class="text-xs font-semibold
          {status === 'critical' ? 'text-sev-critical' : ''}
          {status === 'anomaly' ? 'text-sev-anomaly' : ''}
          {status === 'warning' ? 'text-sev-warning' : ''}
          {status === 'notice' ? 'text-sev-notice' : ''}
          {status === 'info' ? 'text-sev-info' : ''}"
        >{statusLabel(status)}</span>
      </div>
      <div class="mt-1 mono text-[12px] text-muted">
        pinch_id: {node.pinch_id} · layer: {node.layer ?? 'Undefined'}
      </div>
      <div class="mono mt-0.5 text-[11.5px] text-muted">
        ↳ {basename(node.source_file)} · {node.source_function}
      </div>
    </header>

    <section class="grid grid-cols-2 gap-4 md:grid-cols-5">
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Signals</div>
        <div class="mt-1 text-2xl font-semibold tabular-nums">{node.signal_count}</div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Last seen</div>
        <div class="mt-1 text-sm">{relativeTime(node.last_seen, $now)}</div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Critical</div>
        <div class="mt-1 text-2xl font-semibold tabular-nums text-sev-critical">{counts.critical}</div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Anomaly / Warning</div>
        <div class="mt-1 text-sm">
          <span class="text-sev-anomaly">{counts.anomaly}</span> · <span class="text-sev-warning">{counts.warning}</span>
        </div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Clean</div>
        <div class="mt-1 text-2xl font-semibold tabular-nums text-muted">{clean}</div>
      </div>
    </section>

    <section class="card">
      <div class="border-b border-border px-4 py-2 text-sm font-medium">Recent signals</div>
      <div class="max-h-[500px] overflow-y-auto">
        {#each $signals.slice(0, 100) as e (e.received_at)}
          <SignalRow event={e} now={$now} />
        {/each}
        {#if $signals.length === 0}
          <div class="p-6 text-center text-xs text-muted">No signals yet.</div>
        {/if}
      </div>
    </section>
  </div>
{/if}
