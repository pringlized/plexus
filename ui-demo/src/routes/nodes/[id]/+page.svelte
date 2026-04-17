<script lang="ts">
  import { page } from '$app/stores';
  import { ArrowLeft } from 'lucide-svelte';
  import HealthDot from '$lib/components/HealthDot.svelte';
  import SignalRow from '$lib/components/SignalRow.svelte';
  import Sparkline from '$lib/components/Sparkline.svelte';
  import { nodes, signalsByNode, nodeHealth, receptors, sim } from '$lib/sim/store.svelte';
  import { healthLabel, relativeTime } from '$lib/util';

  const nodeId = $derived($page.params.id);
  const node = $derived(nodes.find((n) => n.id === nodeId));
  const health = $derived(node ? nodeHealth(node.id) : 'healthy');
  const signals = $derived(node ? signalsByNode(node.id, 100) : []);
  const counts = $derived(() => {
    const c = { info: 0, notice: 0, warning: 0, anomaly: 0, critical: 0 };
    for (const s of signals) c[s.severity] += 1;
    return c;
  });
  const wired = $derived(
    node
      ? receptors.filter((r) => r.listensTo === '*' || r.listensTo.includes(node.id))
      : []
  );
  const last = $derived(signals[0]);
</script>

{#if !node}
  <div class="p-6 text-sm text-muted">Node not found.</div>
{:else}
  <div class="flex flex-col gap-4 p-6">
    <header class="card px-5 py-4">
      <div class="mb-1 flex items-center gap-2 text-xs text-muted">
        <a href="/" class="inline-flex items-center gap-1 hover:text-accent"><ArrowLeft size={12} /> Back</a>
      </div>
      <div class="flex items-center gap-3">
        <h1 class="text-xl font-semibold">{node.name}</h1>
        <HealthDot health={health} />
        <span class="text-xs font-semibold
          {health === 'healthy' ? 'text-sev-healthy' : ''}
          {health === 'warning' ? 'text-sev-warning' : ''}
          {health === 'anomaly' ? 'text-sev-anomaly' : ''}
          {health === 'critical' ? 'text-sev-critical' : ''}"
        >{healthLabel(health)}</span>
      </div>
      <div class="mt-1 mono text-[12px] text-muted">{node.type} · {node.id} · {node.layer} layer</div>
      <p class="mt-2 text-sm text-muted">{node.description}</p>
    </header>

    <section class="grid grid-cols-2 gap-4 md:grid-cols-5">
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Signals (recent window)</div>
        <div class="mt-1 text-2xl font-semibold tabular-nums">{signals.length}</div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Last signal</div>
        <div class="mt-1 text-sm">{last ? relativeTime(last.timestamp, sim.now) : '—'}</div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Critical</div>
        <div class="mt-1 text-2xl font-semibold tabular-nums text-sev-critical">{counts().critical}</div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Anomaly / Warning</div>
        <div class="mt-1 text-sm"><span class="text-sev-anomaly">{counts().anomaly}</span> · <span class="text-sev-warning">{counts().warning}</span></div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Clean</div>
        <div class="mt-1 text-2xl font-semibold tabular-nums text-muted">{counts().info + counts().notice}</div>
      </div>
    </section>

    <section class="card px-5 py-4">
      <div class="mb-2 flex items-center justify-between">
        <span class="text-sm font-medium">Signal activity · last hour</span>
        <span class="text-xs text-muted">1m buckets</span>
      </div>
      <Sparkline nodeId={node.id} />
    </section>

    <section class="card px-5 py-4">
      <div class="mb-2 text-sm font-medium">Wired to</div>
      <div class="flex flex-wrap gap-2">
        {#each wired as r}
          <a href={`/receptors/${r.id}`} class="chip bg-surface-2 text-muted hover:text-accent">
            {r.name}
          </a>
        {/each}
      </div>
    </section>

    <section class="card">
      <div class="border-b border-border px-4 py-2 text-sm font-medium">Recent signals</div>
      <div class="max-h-[500px] overflow-y-auto">
        {#each signals as s (s.signal_id)}
          <SignalRow signal={s} />
        {/each}
        {#if signals.length === 0}
          <div class="p-6 text-center text-xs text-muted">No signals yet.</div>
        {/if}
      </div>
    </section>
  </div>
{/if}
