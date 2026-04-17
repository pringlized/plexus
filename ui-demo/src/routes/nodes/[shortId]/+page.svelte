<script lang="ts">
  import { ArrowLeft } from 'lucide-svelte';
  import HealthDot from '$lib/components/HealthDot.svelte';
  import Sparkline from '$lib/components/Sparkline.svelte';

  let { data } = $props();
</script>

<div class="flex flex-col gap-4 p-6">
  <header class="card px-5 py-4">
    <div class="mb-1 flex items-center gap-2 text-xs text-muted">
      <a href="/nodes" class="inline-flex items-center gap-1 hover:text-accent"><ArrowLeft size={12} /> All nodes</a>
    </div>
    <div class="flex items-center gap-3">
      <h1 class="text-xl font-semibold">{data.shortId}</h1>
      <HealthDot health="healthy" pulse={false} />
      <span class="text-xs font-semibold text-sev-healthy">HEALTHY</span>
    </div>
    <div class="mt-1 mono text-[12px] text-muted">
      {data.node.type} · {data.node.uuid} · {data.node.layer} layer
    </div>
    <p class="mt-2 text-sm text-muted">{data.node.description}</p>
  </header>

  <section class="grid grid-cols-2 gap-4 md:grid-cols-5">
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Signals</div>
      <div class="mt-1 text-2xl font-semibold tabular-nums">0</div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Last signal</div>
      <div class="mt-1 text-sm text-muted">—</div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Critical</div>
      <div class="mt-1 text-2xl font-semibold tabular-nums text-muted">0</div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Anomaly / Warning</div>
      <div class="mt-1 text-sm text-muted">0 · 0</div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Clean</div>
      <div class="mt-1 text-2xl font-semibold tabular-nums text-muted">0</div>
    </div>
  </section>

  <section class="card px-5 py-4">
    <div class="mb-2 flex items-center justify-between">
      <span class="text-sm font-medium">Signal activity · last hour</span>
      <span class="text-xs text-muted">Waiting for signals</span>
    </div>
    <Sparkline />
  </section>

  <section class="card px-5 py-4">
    <div class="mb-2 text-sm font-medium">Wired to</div>
    {#if data.wiredReceptors.length === 0}
      <div class="text-xs text-muted">No receptors are listening to this node.</div>
    {:else}
      <div class="flex flex-wrap gap-2">
        {#each data.wiredReceptors as r}
          <a href={`/receptors/${r.id}`} class="chip bg-surface-2 text-muted hover:text-accent">
            {r.id}
          </a>
        {/each}
      </div>
    {/if}
  </section>

  <section class="card">
    <div class="border-b border-border px-4 py-2 text-sm font-medium">Recent signals</div>
    <div class="p-6 text-center text-xs text-muted">No signals yet.</div>
  </section>
</div>
