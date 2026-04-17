<script lang="ts">
  import { ArrowLeft } from 'lucide-svelte';

  let { data } = $props();
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
      <div class="mt-1 text-2xl font-semibold tabular-nums">0</div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Successful</div>
      <div class="mt-1 text-2xl font-semibold tabular-nums text-muted">0</div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Receipts</div>
      <div class="mt-1 text-2xl font-semibold tabular-nums">0</div>
    </div>
    <div class="card px-4 py-3">
      <div class="text-xs text-muted">Avg response</div>
      <div class="mt-1 text-sm text-muted">—</div>
    </div>
  </section>

  <section class="card">
    <div class="border-b border-border px-4 py-2 text-sm font-medium">Recent actions</div>
    <div class="p-6 text-center text-xs text-muted">No actions yet.</div>
  </section>

  <section class="card">
    <div class="border-b border-border px-4 py-2 text-sm font-medium">Recent receipts</div>
    <div class="p-6 text-center text-xs text-muted">No receipts yet.</div>
  </section>
</div>
