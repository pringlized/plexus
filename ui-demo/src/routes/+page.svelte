<script lang="ts">
  import { goto } from '$app/navigation';
  import { Pause, Play, Activity, Radar, Cpu, TriangleAlert } from 'lucide-svelte';
  import HealthDot from '$lib/components/HealthDot.svelte';
  import SignalRow from '$lib/components/SignalRow.svelte';
  import { sim, layerHealth, activeAnomalies, nodes, receptors, togglePause } from '$lib/sim/store.svelte';
  import { LAYERS } from '$lib/sim/fixtures';
  import { healthLabel } from '$lib/util';

  const anomalies = $derived(activeAnomalies());
  const layerStates = $derived(
    LAYERS.map((l) => ({ ...l, health: layerHealth(l.id), nodeCount: nodes.filter((n) => n.layer === l.id).length }))
  );
  const feed = $derived(sim.signals.slice(0, 80));
</script>

<div class="flex flex-col gap-6 p-6">
  <section>
    <div class="mb-3 flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold tracking-wide">System Health</h1>
        <p class="text-sm text-muted">Live layer status derived from node signals in the last 10 seconds.</p>
      </div>
    </div>
    <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
      {#each layerStates as l (l.id)}
        <button
          type="button"
          onclick={() => goto(`/monitor?layer=${l.id}`)}
          class="card flex flex-col gap-2 px-5 py-4 text-left transition hover:border-accent/60
            {l.health === 'critical' ? 'ring-1 ring-sev-critical/50' : ''}
            {l.health === 'anomaly' ? 'ring-1 ring-sev-anomaly/40' : ''}
            {l.health === 'warning' ? 'ring-1 ring-sev-warning/40' : ''}"
        >
          <div class="flex items-center justify-between">
            <span class="text-base font-medium">{l.name} Layer</span>
            <HealthDot health={l.health} />
          </div>
          <div class="flex items-baseline gap-2">
            <span class="text-sm font-semibold
              {l.health === 'healthy' ? 'text-sev-healthy' : ''}
              {l.health === 'warning' ? 'text-sev-warning' : ''}
              {l.health === 'anomaly' ? 'text-sev-anomaly' : ''}
              {l.health === 'critical' ? 'text-sev-critical' : ''}"
            >
              {healthLabel(l.health)}
            </span>
            <span class="text-xs text-muted">{l.nodeCount} nodes</span>
          </div>
          <p class="text-xs text-muted">{l.blurb}</p>
        </button>
      {/each}
    </div>
  </section>

  <section class="grid grid-cols-2 gap-4 md:grid-cols-4">
    <div class="card px-5 py-4">
      <div class="flex items-center gap-2 text-muted"><Cpu size={14}/>Nodes</div>
      <div class="mt-2 text-2xl font-semibold tabular-nums">{nodes.length}</div>
      <div class="text-xs text-muted">Active emitters</div>
    </div>
    <div class="card px-5 py-4">
      <div class="flex items-center gap-2 text-muted"><Radar size={14}/>Receptors</div>
      <div class="mt-2 text-2xl font-semibold tabular-nums">{receptors.length}</div>
      <div class="text-xs text-muted">Wired subscribers</div>
    </div>
    <div class="card px-5 py-4">
      <div class="flex items-center gap-2 text-muted"><Activity size={14}/>Signals today</div>
      <div class="mt-2 text-2xl font-semibold tabular-nums">{sim.totalToday.toLocaleString()}</div>
      <div class="text-xs text-muted">{sim.criticalToday} critical · {sim.anomalyToday} anomaly</div>
    </div>
    <div class="card px-5 py-4
      {anomalies > 0 ? 'ring-1 ring-sev-critical/40' : ''}"
    >
      <div class="flex items-center gap-2 text-muted"><TriangleAlert size={14}/>Active anomalies</div>
      <div class="mt-2 text-2xl font-semibold tabular-nums {anomalies > 0 ? 'text-sev-critical' : ''}">{anomalies}</div>
      <div class="text-xs text-muted">Nodes with live anomaly/critical</div>
    </div>
  </section>

  <section class="card flex min-h-0 flex-1 flex-col">
    <div class="flex items-center justify-between border-b border-border px-4 py-2.5">
      <div class="flex items-center gap-2">
        <span class="text-sm font-medium">Live Signal Feed</span>
        <span class="text-xs text-muted">· newest first</span>
      </div>
      <button
        type="button"
        onclick={togglePause}
        class="inline-flex items-center gap-1 rounded border border-border px-2 py-1 text-xs text-muted transition hover:text-text"
      >
        {#if sim.paused}
          <Play size={12}/> Resume
          {#if sim.queuedWhilePaused > 0}<span class="rounded bg-sev-critical/20 px-1.5 text-sev-critical">{sim.queuedWhilePaused}</span>{/if}
        {:else}
          <Pause size={12}/> Pause
        {/if}
      </button>
    </div>
    <div class="max-h-[calc(100vh-22rem)] min-h-[280px] flex-1 overflow-y-auto">
      {#each feed as s (s.signal_id)}
        <div class="animate-slide-in">
          <SignalRow signal={s} />
        </div>
      {/each}
      {#if feed.length === 0}
        <div class="p-6 text-center text-sm text-muted">No signals yet. The simulation primes on load.</div>
      {/if}
    </div>
  </section>
</div>
