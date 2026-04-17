<script lang="ts">
  import type { Severity } from '$lib/types';
  import { severityClass } from '$lib/util';

  let {
    severity,
    pulse = false,
    size = 'md'
  }: { severity: Severity; pulse?: boolean; size?: 'sm' | 'md' } = $props();

  const pulseClass = $derived(
    pulse
      ? severity === 'critical'
        ? 'animate-pulse-strong'
        : severity === 'anomaly' || severity === 'warning'
          ? 'animate-pulse'
          : ''
      : ''
  );
</script>

<span
  class="chip {severityClass(severity)} {pulseClass} {size === 'sm' ? 'px-1.5 py-0 text-[10px]' : ''}"
>
  <span class="h-1.5 w-1.5 rounded-full bg-current"></span>
  {severity.toUpperCase()}
</span>
