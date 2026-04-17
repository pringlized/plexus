<script lang="ts">
  import { Handle, Position, type NodeProps } from '@xyflow/svelte';
  import { sim } from '$lib/sim/store.svelte';
  import type { Receptor } from '$lib/sim/types';
  import { Radar } from 'lucide-svelte';

  let props: NodeProps<{ receptor: Receptor }> = $props();
  const receptor = $derived(props.data.receptor);
  const recentReceipt = $derived(sim.receipts.find((r) => r.receptor_id === receptor.id));
  const recentAge = $derived(recentReceipt ? sim.now - recentReceipt.timestamp : Infinity);
  const pulsing = $derived(recentAge < 1200);
</script>

<div
  class="w-[200px] rounded-lg border border-border bg-surface-2 px-3 py-2 shadow-sm transition
    {pulsing ? 'border-accent/70 ring-2 ring-accent/40' : ''}"
>
  <div class="flex items-center gap-2">
    <Radar size={12} class="text-accent" />
    <span class="truncate text-[12.5px] font-semibold">{receptor.name}</span>
    {#if pulsing}
      <span class="ml-auto inline-flex h-1.5 w-1.5 animate-ping rounded-full bg-accent"></span>
    {/if}
  </div>
  <div class="mt-1.5 flex items-center gap-1.5 text-[10.5px] text-muted">
    <span class="mono">{receptor.type}</span>
    <span>·</span>
    <span class="mono">{receptor.id}</span>
  </div>
  <Handle type="target" position={Position.Left} class="!h-2 !w-2 !border-0 !bg-accent/60" />
</div>
