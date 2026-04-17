<script lang="ts">
  import { Handle, Position, type NodeProps } from '@xyflow/svelte';
  import { Zap } from 'lucide-svelte';
  import { actionEvents, now } from '$lib/stores/signals';
  import type { ActionConfig } from '$lib/types';

  let props: NodeProps<{ action: ActionConfig }> = $props();
  const action = $derived(props.data.action);

  // Pulsing if this action fired in the last 1.2s
  const lastFire = $derived(
    $actionEvents.find((e) => e.action_result?.actions_fired.includes(action.name))
  );
  const recentAge = $derived(lastFire ? $now - lastFire.received_at : Infinity);
  const pulsing = $derived(recentAge < 1200);
</script>

<div
  class="w-[180px] rounded-lg border border-border bg-surface-2 px-3 py-2 shadow-sm transition
    {pulsing ? 'border-accent/70 ring-2 ring-accent/40' : ''}
    {!action.enabled ? 'opacity-60' : ''}"
>
  <div class="flex items-center gap-2">
    <Zap size={12} class="text-accent" />
    <span class="truncate text-[12.5px] font-semibold">{action.name}</span>
    {#if pulsing}
      <span class="ml-auto inline-flex h-1.5 w-1.5 animate-ping rounded-full bg-accent"></span>
    {/if}
  </div>
  <div class="mt-1 text-[10px] uppercase tracking-wider text-muted/80">
    action {action.enabled ? '' : '· disabled'}
  </div>
  <Handle type="target" position={Position.Left} class="!h-2 !w-2 !border-0 !bg-accent/60" />
  <Handle type="source" position={Position.Right} class="!h-2 !w-2 !border-0 !bg-accent/40" />
</div>
