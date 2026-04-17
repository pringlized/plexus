<script lang="ts">
  import { Handle, Position, type NodeProps } from '@xyflow/svelte';
  import { Layers } from 'lucide-svelte';
  import { actionEvents, now } from '$lib/stores/signals';
  import type { BatchConfig } from '$lib/types';

  let props: NodeProps<{ batch: BatchConfig }> = $props();
  const batch = $derived(props.data.batch);

  const lastFire = $derived(
    $actionEvents.find((e) => e.action_result?.batch === batch.name)
  );
  const recentAge = $derived(lastFire ? $now - lastFire.received_at : Infinity);
  const pulsing = $derived(recentAge < 1200);
</script>

<div
  class="w-[200px] rounded-lg border border-border bg-surface-2 px-3 py-2 shadow-sm transition
    {pulsing ? 'border-accent/80 ring-2 ring-accent/50' : ''}"
>
  <div class="flex items-center gap-2">
    <Layers size={12} class="text-accent" />
    <span class="truncate text-[12.5px] font-semibold">{batch.name}</span>
    {#if pulsing}
      <span class="ml-auto inline-flex h-1.5 w-1.5 animate-ping rounded-full bg-accent"></span>
    {/if}
  </div>
  <div class="mt-1 text-[10px] uppercase tracking-wider text-muted/80">
    batch · {batch.actions.length} {batch.actions.length === 1 ? 'action' : 'actions'}
  </div>
  <Handle type="target" position={Position.Left} class="!h-2 !w-2 !border-0 !bg-accent/60" />
  <Handle type="source" position={Position.Right} class="!h-2 !w-2 !border-0 !bg-accent/40" />
</div>
