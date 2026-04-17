<script lang="ts">
  import { statusDot, type LayerStatus } from '$lib/util';

  let { status, pulse = true }: { status: LayerStatus; pulse?: boolean } = $props();
</script>

<span class="relative inline-flex h-2.5 w-2.5 items-center justify-center">
  {#if pulse && status !== 'healthy' && status !== 'info'}
    <span class="absolute inline-flex h-full w-full animate-ping rounded-full opacity-60 {statusDot(status)}"></span>
  {/if}
  <span class="relative inline-flex h-2.5 w-2.5 rounded-full {statusDot(status)}"></span>
</span>
