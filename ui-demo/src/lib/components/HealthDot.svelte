<script lang="ts">
  import type { LayerHealth } from '$lib/sim/types';
  import { healthDot } from '$lib/util';

  let { health, pulse = true }: { health: LayerHealth; pulse?: boolean } = $props();
</script>

<span class="relative inline-flex h-2.5 w-2.5 items-center justify-center">
  {#if pulse && health !== 'healthy'}
    <span class="absolute inline-flex h-full w-full animate-ping rounded-full opacity-60 {healthDot(health)}"></span>
  {/if}
  <span class="relative inline-flex h-2.5 w-2.5 rounded-full {healthDot(health)}"></span>
</span>
