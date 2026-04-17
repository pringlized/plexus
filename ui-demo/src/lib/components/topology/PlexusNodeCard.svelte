<script lang="ts">
  import { Cpu } from 'lucide-svelte';
  import { Handle, Position, type NodeProps } from '@xyflow/svelte';
  import { now, signalsForNode } from '$lib/stores/signals';
  import { statusDot } from '$lib/util';
  import type { NodeSummary } from '$lib/types';

  let props: NodeProps<{ node: NodeSummary }> = $props();
  const node = $derived(props.data.node);

  const recentSignals = $derived(signalsForNode(node.pinch_id));
  const lastEvent = $derived($recentSignals[0]);
  const recentAge = $derived(lastEvent ? $now - lastEvent.received_at : Infinity);
  const pulsing = $derived(recentAge < 1200);
  const status = $derived(node.last_severity);
  const critical = $derived(status === 'critical');
</script>

<div
  class="relative w-[200px] rounded-lg border bg-surface px-3 py-2 shadow-sm transition
    {critical ? 'border-sev-critical ring-2 ring-sev-critical/50 animate-pulse-strong' : 'border-border'}
    {status === 'anomaly' && !critical ? 'border-sev-anomaly ring-1 ring-sev-anomaly/40' : ''}
    {status === 'warning' && !critical ? 'border-sev-warning ring-1 ring-sev-warning/40' : ''}"
>
  <div class="flex items-center gap-2">
    <span class="inline-flex h-2.5 w-2.5 rounded-full {statusDot(status)}"></span>
    <span class="truncate text-[12.5px] font-semibold">
      {node.name ?? node.pinch_id.slice(0, 8)}
    </span>
    {#if pulsing}
      <span class="ml-auto inline-flex h-1.5 w-1.5 animate-ping rounded-full bg-accent/70"></span>
    {/if}
  </div>
  <div class="mt-1.5 flex items-center gap-1.5 text-[10.5px] text-muted">
    <Cpu size={11} />
    <span class="mono truncate">{node.source_function}</span>
  </div>
  <div class="mono truncate text-[9.5px] text-muted/70">{node.pinch_id}</div>
  <Handle type="source" position={Position.Right} class="!h-2 !w-2 !border-0 !bg-accent/60" />
</div>
