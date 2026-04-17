<script lang="ts">
  import { goto } from '$app/navigation';
  import { Activity, Cpu, TriangleAlert, Zap } from 'lucide-svelte';
  import HealthDot from '$lib/components/HealthDot.svelte';
  import SignalRow from '$lib/components/SignalRow.svelte';
  import {
    signalEvents,
    layerHealth,
    activeAnomalies,
    nodes,
    nodesByLayer,
    now
  } from '$lib/stores/signals';
  import { statusLabel } from '$lib/util';

  let { data } = $props();

  const layers = $derived(Array.from($nodesByLayer.entries()));
  const total = $derived($signalEvents.length);
  const critical = $derived($signalEvents.filter((e) => e.severity === 'critical').length);
  const anomaly = $derived($signalEvents.filter((e) => e.severity === 'anomaly').length);
  const feed = $derived($signalEvents.slice(0, 80));
</script>

<div class="flex flex-col gap-6 p-6">
  <section>
    <div class="mb-3">
      <h1 class="text-lg font-semibold tracking-wide">System Health</h1>
      <p class="text-sm text-muted">
        Live layer status derived from node signals in the last 10 seconds. Layers
        emerge from the signal stream — nothing pre-declared.
      </p>
    </div>
    {#if layers.length === 0}
      <div class="card flex h-32 items-center justify-center text-sm text-muted">
        No nodes yet. Waiting for first signal…
      </div>
    {:else}
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {#each layers as [layer, layerNodes] (layer)}
          {@const status = $layerHealth[layer] ?? 'healthy'}
          <button
            type="button"
            onclick={() => goto(`/monitor?layer=${encodeURIComponent(layer)}`)}
            class="card flex flex-col gap-2 px-5 py-4 text-left transition hover:border-accent/60
              {status === 'critical' ? 'ring-1 ring-sev-critical/50' : ''}
              {status === 'anomaly' ? 'ring-1 ring-sev-anomaly/40' : ''}
              {status === 'warning' ? 'ring-1 ring-sev-warning/40' : ''}"
          >
            <div class="flex items-center justify-between">
              <span class="text-base font-medium capitalize">{layer} Layer</span>
              <HealthDot {status} />
            </div>
            <div class="flex items-baseline gap-2">
              <span
                class="text-sm font-semibold
                {status === 'healthy' ? 'text-sev-healthy' : ''}
                {status === 'warning' ? 'text-sev-warning' : ''}
                {status === 'anomaly' ? 'text-sev-anomaly' : ''}
                {status === 'critical' ? 'text-sev-critical' : ''}"
              >
                {statusLabel(status)}
              </span>
              <span class="text-xs text-muted">
                {layerNodes.length} {layerNodes.length === 1 ? 'node' : 'nodes'}
              </span>
            </div>
          </button>
        {/each}
      </div>
    {/if}
  </section>

  <section class="grid grid-cols-2 gap-4 md:grid-cols-4">
    <div class="card px-5 py-4">
      <div class="flex items-center gap-2 text-muted"><Cpu size={14}/>Nodes</div>
      <div class="mt-2 text-2xl font-semibold tabular-nums">{$nodes.length}</div>
      <div class="text-xs text-muted">Active emitters</div>
    </div>
    <div class="card px-5 py-4">
      <div class="flex items-center gap-2 text-muted"><Zap size={14}/>Actions</div>
      <div class="mt-2 text-2xl font-semibold tabular-nums">{data.actions.length}</div>
      <div class="text-xs text-muted">Registered</div>
    </div>
    <div class="card px-5 py-4">
      <div class="flex items-center gap-2 text-muted"><Activity size={14}/>Signals received</div>
      <div class="mt-2 text-2xl font-semibold tabular-nums">{total.toLocaleString()}</div>
      <div class="text-xs text-muted">{critical} critical · {anomaly} anomaly</div>
    </div>
    <div class="card px-5 py-4 {$activeAnomalies > 0 ? 'ring-1 ring-sev-critical/40' : ''}">
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
      {#each feed as e (e.pinch_id + '-' + e.received_at)}
        <div class="animate-slide-in"><SignalRow event={e} now={$now} /></div>
      {/each}
      {#if feed.length === 0}
        <div class="flex min-h-[240px] items-center justify-center text-sm text-muted">
          Waiting for signals…
        </div>
      {/if}
    </div>
  </section>
</div>
