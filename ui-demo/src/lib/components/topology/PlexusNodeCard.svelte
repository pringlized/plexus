<script lang="ts">
  import { Handle, Position, type NodeProps } from '@xyflow/svelte';
  import { healthDot } from '$lib/util';
  import type { NodeConfig, HealthStatus } from '$lib/types';
  import { Cpu } from 'lucide-svelte';

  let props: NodeProps<{
    shortId: string;
    node: NodeConfig;
    health?: HealthStatus;
    pulsing?: boolean;
  }> = $props();

  const shortId = $derived(props.data.shortId);
  const node = $derived(props.data.node);
  const health = $derived<HealthStatus>(props.data.health ?? 'healthy');
  const pulsing = $derived(props.data.pulsing ?? false);
  const critical = $derived(health === 'critical');
</script>

<div
  class="relative w-[200px] rounded-lg border bg-surface px-3 py-2 shadow-sm transition
    {critical ? 'border-sev-critical ring-2 ring-sev-critical/50 animate-pulse-strong' : 'border-border'}
    {health === 'anomaly' && !critical ? 'border-sev-anomaly ring-1 ring-sev-anomaly/40' : ''}
    {health === 'warning' && !critical ? 'border-sev-warning ring-1 ring-sev-warning/40' : ''}"
>
  <div class="flex items-center gap-2">
    <span class="inline-flex h-2.5 w-2.5 rounded-full {healthDot(health)}"></span>
    <span class="truncate text-[12.5px] font-semibold">{shortId}</span>
    {#if pulsing}
      <span class="ml-auto inline-flex h-1.5 w-1.5 animate-ping rounded-full bg-accent/70"></span>
    {/if}
  </div>
  <div class="mt-1.5 flex items-center gap-1.5 text-[10.5px] text-muted">
    <Cpu size={11} />
    <span class="mono">{node.type}</span>
    <span>·</span>
    <span class="mono truncate">{node.uuid.slice(0, 8)}…</span>
  </div>
  <Handle type="source" position={Position.Right} class="!h-2 !w-2 !border-0 !bg-accent/60" />
  <Handle type="target" position={Position.Left} class="!h-2 !w-2 !border-0 !bg-muted/50" />
</div>
