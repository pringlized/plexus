<script lang="ts">
  // Idle component — takes a pre-computed bucket array. Empty bucket list
  // renders as a flat grey baseline, which is the honest state before any
  // signals have flowed.

  export interface Bucket {
    count: number;
    maxSev: number; // 0..4 = info..critical
  }

  let { bins = [] as Bucket[] }: { bins?: Bucket[] } = $props();

  const max = $derived(Math.max(1, ...bins.map((b) => b.count)));

  const sevColor = [
    'var(--sev-info)',
    'var(--sev-notice)',
    'var(--sev-warning)',
    'var(--sev-anomaly)',
    'var(--sev-critical)'
  ];
</script>

<div class="flex h-14 items-end gap-[1.5px]">
  {#if bins.length === 0}
    <div class="flex h-full w-full items-end">
      <div class="h-[2px] w-full rounded bg-border"></div>
    </div>
  {:else}
    {#each bins as b}
      {@const h = Math.max(2, Math.round((b.count / max) * 100))}
      <div
        class="w-[3px] flex-1 rounded-[1px] transition"
        style="height: {h}%; background: rgb({b.count ? sevColor[b.maxSev] : 'var(--border)'});"
        title={`${b.count} signals`}
      ></div>
    {/each}
  {/if}
</div>
