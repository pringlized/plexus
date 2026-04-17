<script lang="ts">
  import { goto } from '$app/navigation';
  import { Activity, Radar, Cpu, TriangleAlert } from 'lucide-svelte';
  import HealthDot from '$lib/components/HealthDot.svelte';
  import SignalRow from '$lib/components/SignalRow.svelte';
  import { deriveLayers } from '$lib/config-helpers';
  import { signalEvents, activeAnomalies, layerHealth, now } from '$lib/stores/signals';
  import { healthLabel } from '$lib/util';
  import type { HealthStatus } from '$lib/types';

  let { data } = $props();

  const layers = $derived(deriveLayers(data.nodes));
  const nodeCount = $derived(Object.keys(data.nodes).length);
  const receptorCount = $derived(Object.keys(data.receptors).length);

  const total = $derived($signalEvents.length);
  const critical = $derived($signalEvents.filter((e) => e.signal.severity === 'critical').length);
  const anomaly = $derived($signalEvents.filter((e) => e.signal.severity === 'anomaly').length);
  const feed = $derived($signalEvents.slice(0, 80));

  function layerStatus(layerName: string): HealthStatus {
    return $layerHealth[layerName] ?? 'healthy';
  }
</script>

<div class="flex flex-col gap-6 p-6">
  <section>
    <div class="mb-3 flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold tracking-wide">System Health</h1>
        <p class="text-sm text-muted">Live layer status from signals in the last 10 seconds.</p>
      </div>
    </div>
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {#each layers as l (l.name)}
        {@const h = layerStatus(l.name)}
        <button
          type="button"
          onclick={() => goto(`/monitor?layer=${l.name}`)}
          class="card flex flex-col gap-2 px-5 py-4 text-left transition hover:border-accent/60
            {h === 'critical' ? 'ring-1 ring-sev-critical/50' : ''}
            {h === 'anomaly' ? 'ring-1 ring-sev-anomaly/40' : ''}
            {h === 'warning' ? 'ring-1 ring-sev-warning/40' : ''}"
        >
          <div class="flex items-center justify-between">
            <span class="text-base font-medium capitalize">{l.name} Layer</span>
            <HealthDot health={h} />
          </div>
          <div class="flex items-baseline gap-2">
            <span
              class="text-sm font-semibold
              {h === 'healthy' ? 'text-sev-healthy' : ''}
              {h === 'warning' ? 'text-sev-warning' : ''}
              {h === 'anomaly' ? 'text-sev-anomaly' : ''}
              {h === 'critical' ? 'text-sev-critical' : ''}"
            >
              {healthLabel(h)}
            </span>
            <span class="text-xs text-muted">{l.nodes.length} {l.nodes.length === 1 ? 'node' : 'nodes'}</span>
          </div>
          <p class="text-xs text-muted">{l.description}</p>
        </button>
      {/each}
    </div>
  </section>

  <section class="grid grid-cols-2 gap-4 md:grid-cols-4">
    <div class="card px-5 py-4">
      <div class="flex items-center gap-2 text-muted"><Cpu size={14}/>Nodes</div>
      <div class="mt-2 text-2xl font-semibold tabular-nums">{nodeCount}</div>
      <div class="text-xs text-muted">Configured emitters</div>
    </div>
    <div class="card px-5 py-4">
      <div class="flex items-center gap-2 text-muted"><Radar size={14}/>Receptors</div>
      <div class="mt-2 text-2xl font-semibold tabular-nums">{receptorCount}</div>
      <div class="text-xs text-muted">Wired subscribers</div>
    </div>
    <div class="card px-5 py-4">
      <div class="flex items-center gap-2 text-muted"><Activity size={14}/>Signals received</div>
      <div class="mt-2 text-2xl font-semibold tabular-nums">{total.toLocaleString()}</div>
      <div class="text-xs text-muted">{critical} critical · {anomaly} anomaly</div>
    </div>
    <div
      class="card px-5 py-4
      {$activeAnomalies > 0 ? 'ring-1 ring-sev-critical/40' : ''}"
    >
      <div class="flex items-center gap-2 text-muted"><TriangleAlert size={14}/>Active anomalies</div>
      <div class="mt-2 text-2xl font-semibold tabular-nums {$activeAnomalies > 0 ? 'text-sev-critical' : ''}">
        {$activeAnomalies}
      </div>
      <div class="text-xs text-muted">Anomaly/critical within 10s</div>
    </div>
  </section>

  <section class="card flex min-h-0 flex-1 flex-col">
    <div class="flex items-center justify-between border-b border-border px-4 py-2.5">
      <div class="flex items-center gap-2">
        <span class="text-sm font-medium">Live Signal Feed</span>
        <span class="text-xs text-muted">· newest first</span>
      </div>
    </div>
    <div class="max-h-[calc(100vh-22rem)] min-h-[280px] flex-1 overflow-y-auto">
      {#each feed as e (e.signal.signal_id)}
        <div class="animate-slide-in">
          <SignalRow event={e} now={$now} />
        </div>
      {/each}
      {#if feed.length === 0}
        <div class="flex min-h-[240px] items-center justify-center text-sm text-muted">
          Waiting for signals…
        </div>
      {/if}
    </div>
  </section>
</div>
