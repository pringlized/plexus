<script lang="ts">
  import { SvelteFlowProvider } from '@xyflow/svelte';
  import Designer from '$lib/components/topology/designer/Designer.svelte';
</script>

<SvelteFlowProvider>
  <Designer />
</SvelteFlowProvider>
