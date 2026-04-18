<script lang="ts">
  import type { NodeProps } from '@xyflow/svelte';
  import { layerHealth } from '$lib/stores/signals';
  import { statusDot } from '$lib/util';

  let props: NodeProps = $props();
  const data = $derived(props.data as unknown as { label: string; layer: string });
  const status = $derived($layerHealth[data.layer] ?? 'healthy');
</script>

<div
  class="h-full w-full rounded-xl border border-dashed border-border bg-surface/30 px-3 py-2 transition
    {status === 'critical' ? 'border-sev-critical/70 bg-sev-critical/5' : ''}
    {status === 'anomaly' ? 'border-sev-anomaly/50 bg-sev-anomaly/5' : ''}"
  style="pointer-events: none"
>
  <div class="flex items-center gap-2 text-[11px] uppercase tracking-[0.15em] text-muted">
    <span class="inline-block h-2 w-2 rounded-full {statusDot(status)}"></span>
    {data.label} Layer
  </div>
</div>
