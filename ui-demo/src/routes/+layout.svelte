<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import { initTheme } from '$lib/theme.svelte';
  import { startSimulation } from '$lib/sim/store.svelte';

  let { children } = $props();

  onMount(() => {
    initTheme();
    startSimulation();
  });
</script>

<div class="flex h-screen w-screen overflow-hidden bg-bg text-text">
  <Sidebar />
  <main class="flex min-w-0 flex-1 flex-col">
    <header class="flex h-12 items-center justify-end gap-2 border-b border-border bg-surface px-4">
      <span class="mr-auto text-xs uppercase tracking-widest text-muted">Demo — simulated signals</span>
      <ThemeToggle />
    </header>
    <div class="flex-1 overflow-y-auto">
      {@render children()}
    </div>
  </main>
</div>
