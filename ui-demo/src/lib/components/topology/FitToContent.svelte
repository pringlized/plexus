<script lang="ts">
  import { useSvelteFlow } from '@xyflow/svelte';

  // Apply a pre-computed viewport (x, y, zoom) to the SvelteFlow canvas.
  // Component sits inside <SvelteFlow> so it has access to the flow context.
  let {
    target
  }: { target: { x: number; y: number; zoom: number } | null } = $props();

  const { setViewport } = useSvelteFlow();

  $effect(() => {
    if (!target) return;
    queueMicrotask(() => {
      try {
        setViewport(target, { duration: 350 });
      } catch {
        // flow not ready yet — ignore
      }
    });
  });
</script>
