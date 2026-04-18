<script lang="ts">
  import { Handle, Position, type NodeProps } from '@xyflow/svelte';
  import { statusDot } from '$lib/util';
  import type { DesignerNode } from './types';

  let props: NodeProps = $props();
  const nodeData = $derived(props.data as unknown as { node: DesignerNode });
  const node = $derived(nodeData.node);
  const selected = $derived(props.selected);
  const critical = $derived(node.last_severity === 'critical');
</script>

<div
  class="relative w-[220px] rounded-lg border bg-surface px-3 py-2 shadow-sm transition
    {selected ? 'border-accent ring-2 ring-accent/70 ring-offset-2 ring-offset-bg' : ''}
    {!selected && critical ? 'border-sev-critical ring-2 ring-sev-critical/40' : ''}
    {!selected && node.last_severity === 'anomaly' && !critical ? 'border-sev-anomaly ring-1 ring-sev-anomaly/40' : ''}
    {!selected && node.last_severity === 'warning' && !critical ? 'border-sev-warning ring-1 ring-sev-warning/40' : ''}
    {!selected && !critical && node.last_severity !== 'anomaly' && node.last_severity !== 'warning' ? 'border-border' : ''}"
>
  <div class="flex items-center gap-2">
    <span class="inline-flex h-2.5 w-2.5 rounded-full {statusDot(node.last_severity)}"></span>
    <span class="truncate text-[12.5px] font-semibold">{node.name}</span>
  </div>
  <div class="mt-1 mono truncate text-[10.5px] text-muted">{node.source_function}</div>
  <div class="mono truncate text-[9.5px] text-muted/70">{node.pinch_id}</div>
  <Handle type="source" position={Position.Right} class="!h-2 !w-2 !border-0 !bg-accent/60" />
</div>
