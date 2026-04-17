<script lang="ts">
  import { Moon, Sun } from 'lucide-svelte';
  import { theme, toggleTheme } from '$lib/theme.svelte';
</script>

<button
  type="button"
  onclick={toggleTheme}
  class="inline-flex h-8 w-8 items-center justify-center rounded-md border border-border bg-surface text-muted transition hover:text-text"
  aria-label="Toggle theme"
>
  {#if theme.mode === 'dark'}
    <Sun size={16} />
  {:else}
    <Moon size={16} />
  {/if}
</button>
