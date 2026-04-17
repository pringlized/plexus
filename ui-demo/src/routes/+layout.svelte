<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import { initTheme } from '$lib/theme.svelte';

  let { data, children } = $props();

  onMount(() => {
    initTheme();
  });
</script>

<div class="flex h-screen w-screen overflow-hidden bg-bg text-text">
  <Sidebar nodes={data.nodes} receptors={data.receptors} />
  <main class="flex min-w-0 flex-1 flex-col">
    <header class="flex h-12 items-center justify-end gap-2 border-b border-border bg-surface px-4">
      <span class="mr-auto text-xs uppercase tracking-widest text-muted">Config-driven — awaiting signals</span>
      <ThemeToggle />
    </header>
    <div class="flex-1 overflow-y-auto">
      {@render children()}
    </div>
  </main>
</div>
