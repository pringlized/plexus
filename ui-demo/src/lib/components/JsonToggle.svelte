<script lang="ts">
  import { ChevronRight } from 'lucide-svelte';

  let { data, label = 'Signal JSON' }: { data: unknown; label?: string } = $props();
  let expanded = $state(false);
</script>

<div class="mt-1">
  <button
    type="button"
    onclick={() => (expanded = !expanded)}
    class="inline-flex items-center gap-0.5 text-[10px] uppercase tracking-wider text-muted hover:text-text"
  >
    <ChevronRight size={10} class={expanded ? 'rotate-90 transition' : 'transition'} />
    {label}
  </button>
  {#if expanded}
    <pre class="mono mt-1 max-h-72 overflow-auto rounded border border-border bg-bg px-2 py-1.5 text-[10.5px] text-text/80">{JSON.stringify(data, null, 2)}</pre>
  {/if}
</div>
