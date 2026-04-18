<script lang="ts">
  import Sidebar from '$lib/components/Sidebar.svelte';
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';

  let { data, children } = $props();
</script>

<div class="flex h-screen w-screen overflow-hidden bg-bg text-text">
  <Sidebar actions={data.actions} batches={data.batches} />
  <main class="flex min-w-0 flex-1 flex-col">
    <header class="flex h-12 items-center justify-end gap-2 border-b border-border bg-surface px-4">
      <span class="mr-auto text-xs uppercase tracking-widest text-muted">Live signals</span>
      <ThemeToggle />
    </header>
    <div class="flex-1 overflow-y-auto">
      {@render children()}
    </div>
  </main>
</div>
