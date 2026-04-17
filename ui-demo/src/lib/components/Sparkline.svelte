<script lang="ts">
  import { sim, severityRank } from '$lib/sim/store.svelte';
  import type { Signal } from '$lib/sim/types';

  let { nodeId, bucketMs = 60_000, buckets = 60 }: { nodeId: string; bucketMs?: number; buckets?: number } = $props();

  const bins = $derived(() => {
    const end = sim.now;
    const start = end - buckets * bucketMs;
    const out = new Array(buckets).fill(0).map((_, i) => ({
      start: start + i * bucketMs,
      count: 0,
      maxSev: 0
    }));
    for (const s of sim.signals as Signal[]) {
      if (s.node_id !== nodeId) continue;
      if (s.timestamp < start || s.timestamp >= end) continue;
      const idx = Math.min(buckets - 1, Math.floor((s.timestamp - start) / bucketMs));
      out[idx].count += 1;
      const sev = severityRank(s.severity);
      if (sev > out[idx].maxSev) out[idx].maxSev = sev;
    }
    return out;
  });

  const max = $derived(Math.max(1, ...bins().map((b) => b.count)));

  const sevColor = ['var(--sev-info)', 'var(--sev-notice)', 'var(--sev-warning)', 'var(--sev-anomaly)', 'var(--sev-critical)'];
</script>

<div class="flex h-14 items-end gap-[1.5px]">
  {#each bins() as b}
    {@const h = Math.max(2, Math.round((b.count / max) * 100))}
    <div
      class="w-[3px] flex-1 rounded-[1px] transition"
      style="height: {h}%; background: rgb({b.count ? sevColor[b.maxSev] : 'var(--border)'});"
      title={`${b.count} signals`}
    ></div>
  {/each}
</div>
