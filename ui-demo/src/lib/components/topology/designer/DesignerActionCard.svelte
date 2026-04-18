<script lang="ts">
  import { Handle, Position, type NodeProps } from '@xyflow/svelte';
  import { Zap } from 'lucide-svelte';
  import type { DesignerAction } from './types';

  let props: NodeProps = $props();
  const actionData = $derived(props.data as unknown as { action: DesignerAction });
  const action = $derived(actionData.action);
  const selected = $derived(props.selected);
</script>

<div
  class="w-[200px] rounded-lg border bg-surface-2 px-3 py-2 shadow-sm transition
    {selected
      ? 'border-accent ring-2 ring-accent/70 ring-offset-2 ring-offset-bg'
      : 'border-border'}
    {!action.enabled ? 'opacity-60' : ''}"
>
  <div class="flex items-center gap-2">
    <Zap size={12} class="text-accent" />
    <span class="truncate text-[12.5px] font-semibold">{action.name}</span>
  </div>
  <div class="mt-1 text-[10px] uppercase tracking-wider text-muted/80">
    Action {action.enabled ? '' : '· disabled'}
  </div>
  <Handle type="target" position={Position.Left} class="!h-2 !w-2 !border-0 !bg-accent/60" />
</div>
