<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { initTheme } from '$lib/theme.svelte';
  import { startStream } from '$lib/stores/stream';

  let { children } = $props();

  // Global setup that runs for every route — including pages that opt out
  // of the standard sidebar/header shell (e.g. the topology designer).
  onMount(() => {
    initTheme();
    startStream();
  });
</script>

{@render children()}
