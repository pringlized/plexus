<script lang="ts">
  import { page } from '$app/stores';
  import { deriveLayers } from '$lib/config-helpers';

  let { data } = $props();

  const layers = $derived(deriveLayers(data.nodes));
  const nodeCount = $derived(Object.keys(data.nodes).length);
  const receptorCount = $derived(Object.keys(data.receptors).length);

  const activeLayerName = $derived($page.url.searchParams.get('layer'));
  const activeLayer = $derived(
    activeLayerName ? layers.find((l) => l.name === activeLayerName) ?? null : null
  );
</script>

<div class="flex h-full flex-col p-6 pb-0">
  <header class="mb-4 flex flex-wrap items-center gap-3">
    <div>
      <h1 class="text-lg font-semibold tracking-wide">Live Signal Monitor</h1>
      <p class="text-sm text-muted">Node broadcasts → receptor receipts → receptor actions. Awaiting signals.</p>
    </div>
    <div class="ml-auto flex items-center gap-3 text-xs text-muted">
      <span>{nodeCount} nodes</span>
      <span>·</span>
      <span>{receptorCount} receptors</span>
      <span>·</span>
      <span>{layers.length} layers</span>
    </div>
  </header>

  {#if activeLayer}
    <div class="mb-4 border-l-2 border-accent/60 pl-3">
      <h2 class="text-base font-semibold capitalize">{activeLayer.name} Layer</h2>
      <p class="text-sm text-muted">{activeLayer.description}</p>
    </div>
  {:else if activeLayerName}
    <div class="mb-4 border-l-2 border-sev-warning/60 pl-3">
      <h2 class="text-base font-semibold capitalize">{activeLayerName} Layer</h2>
      <p class="text-sm text-muted">No nodes currently configured in this layer.</p>
    </div>
  {/if}

  <div class="grid min-h-0 flex-1 grid-cols-3 gap-4 pb-6">
    <section class="card flex min-h-0 flex-col">
      <div class="flex items-center justify-between border-b border-border px-3 py-2">
        <span class="text-xs font-semibold uppercase tracking-wider text-muted">Node Broadcasts</span>
        <span class="text-[10px] text-muted">0</span>
      </div>
      <div class="flex min-h-0 flex-1 items-center justify-center p-6 text-center text-xs text-muted">
        Waiting for signals…
      </div>
    </section>

    <section class="card flex min-h-0 flex-col">
      <div class="flex items-center justify-between border-b border-border px-3 py-2">
        <span class="text-xs font-semibold uppercase tracking-wider text-muted">Receptor Receipts</span>
        <span class="text-[10px] text-muted">0</span>
      </div>
      <div class="flex min-h-0 flex-1 items-center justify-center p-6 text-center text-xs text-muted">
        Receipts will appear here as receptors react to signals.
      </div>
    </section>

    <section class="card flex min-h-0 flex-col">
      <div class="flex items-center justify-between border-b border-border px-3 py-2">
        <span class="text-xs font-semibold uppercase tracking-wider text-muted">Receptor Actions</span>
        <span class="text-[10px] text-muted">0</span>
      </div>
      <div class="flex min-h-0 flex-1 items-center justify-center p-6 text-center text-xs text-muted">
        No actions yet.
      </div>
    </section>
  </div>
</div>
