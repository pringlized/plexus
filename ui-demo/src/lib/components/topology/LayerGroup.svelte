<script lang="ts">
  import type { NodeProps } from '@xyflow/svelte';
  import { sim, layerHealth } from '$lib/sim/store.svelte';
  import type { LayerId } from '$lib/sim/types';
  import { healthDot } from '$lib/util';

  let props: NodeProps<{ label: string; layer: LayerId }> = $props();
  const layer = $derived(props.data.layer);
  const health = $derived(layerHealth(layer));
</script>

<div
  class="h-full w-full rounded-xl border border-dashed border-border bg-surface/30 px-3 py-2 transition
    {health === 'critical' ? 'border-sev-critical/70 bg-sev-critical/5' : ''}
    {health === 'anomaly' ? 'border-sev-anomaly/50 bg-sev-anomaly/5' : ''}"
  style="pointer-events: none"
>
  <div class="flex items-center gap-2 text-[11px] uppercase tracking-[0.15em] text-muted">
    <span class="inline-block h-2 w-2 rounded-full {healthDot(health)}"></span>
    {props.data.label} Layer
  </div>
</div>
