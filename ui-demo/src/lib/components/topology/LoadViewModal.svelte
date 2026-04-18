<script lang="ts">
  import { X, FolderOpen } from 'lucide-svelte';

  export interface SavedViewSummary {
    id: string;
    name: string;
    description: string | null;
    created_at: string;
    updated_at: string;
  }

  let {
    views = [] as SavedViewSummary[],
    currentId = null as string | null,
    loading = false,
    error = null as string | null,
    onload,
    oncancel
  }: {
    views?: SavedViewSummary[];
    /** id of the view currently being shown — disabled in the list. */
    currentId?: string | null;
    loading?: boolean;
    error?: string | null;
    onload: (view: SavedViewSummary) => void;
    oncancel: () => void;
  } = $props();

  let selectedId = $state<string | null>(null);
  const selected = $derived(views.find((v) => v.id === selectedId) ?? null);
  const canLoad = $derived(selected !== null && !loading);

  function submit(e: SubmitEvent) {
    e.preventDefault();
    if (!canLoad || !selected) return;
    onload(selected);
  }

  function onBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) oncancel();
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') oncancel();
  }

  function fmtDate(iso: string): string {
    try {
      return new Date(iso).toLocaleString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return iso;
    }
  }
</script>

<svelte:window onkeydown={onKey} />

<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="load-view-title"
  onclick={onBackdropClick}
  class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
>
  <form
    onsubmit={submit}
    class="w-full max-w-md rounded-xl border border-border bg-surface shadow-2xl"
  >
    <header class="flex items-start justify-between border-b border-border px-5 py-4">
      <div>
        <h2 id="load-view-title" class="text-base font-semibold">Load topology view</h2>
        <p class="mt-0.5 text-xs text-muted">
          Pick a saved canvas to restore.
        </p>
      </div>
      <button
        type="button"
        onclick={oncancel}
        class="-mr-1 -mt-1 inline-flex h-7 w-7 items-center justify-center rounded-md text-muted transition hover:text-text"
        aria-label="Close"
      >
        <X size={14} />
      </button>
    </header>

    <div class="space-y-3 px-5 py-4">
      {#if loading}
        <p class="py-6 text-center text-xs text-muted">Loading saved views…</p>
      {:else if views.length === 0}
        <div class="rounded-md border border-dashed border-border bg-bg/40 px-4 py-8 text-center">
          <FolderOpen size={20} class="mx-auto text-muted" />
          <p class="mt-2 text-sm text-text">No saved topologies yet</p>
          <p class="mt-1 text-xs text-muted">
            Build a canvas and click <span class="text-text">Save View</span> to create one.
          </p>
        </div>
      {:else}
        <ul class="max-h-80 space-y-2 overflow-y-auto pr-1">
          {#each views as v (v.id)}
            {@const isSelected = v.id === selectedId}
            {@const isCurrent = v.id === currentId}
            <li>
              <button
                type="button"
                onclick={() => (selectedId = v.id)}
                disabled={isCurrent}
                class="w-full rounded-md border px-3 py-2 text-left transition
                  {isCurrent
                    ? 'cursor-not-allowed border-border bg-bg/40 opacity-50'
                    : isSelected
                      ? 'border-accent bg-accent/10'
                      : 'border-border bg-bg/40 hover:border-accent/60 hover:bg-bg/60'}"
              >
                <div class="flex items-baseline justify-between gap-2">
                  <div class="flex min-w-0 items-center gap-2">
                    <div class="truncate text-sm font-medium text-text">{v.name}</div>
                    {#if isCurrent}
                      <span class="shrink-0 rounded bg-accent/20 px-1.5 py-0.5 text-[9px] font-medium uppercase tracking-wider text-accent">
                        Currently viewing
                      </span>
                    {/if}
                  </div>
                  {#if v.updated_at}
                    <div class="shrink-0 text-[10px] text-muted">{fmtDate(v.updated_at)}</div>
                  {/if}
                </div>
                {#if v.description}
                  <div class="mt-0.5 truncate text-xs text-muted">{v.description}</div>
                {/if}
              </button>
            </li>
          {/each}
        </ul>
      {/if}

      {#if error}
        <p class="text-xs text-sev-critical">{error}</p>
      {/if}
    </div>

    <footer class="flex items-center justify-end gap-2 border-t border-border px-5 py-3">
      <button
        type="button"
        onclick={oncancel}
        class="rounded-md border border-border bg-surface px-3 py-1.5 text-xs text-muted transition hover:text-text"
      >
        Cancel
      </button>
      {#if views.length > 0}
        <button
          type="submit"
          disabled={!canLoad}
          class="rounded-md border border-accent bg-accent px-3 py-1.5 text-xs font-medium text-bg transition hover:bg-accent/90 disabled:opacity-50"
        >
          {loading ? 'Loading…' : 'Load'}
        </button>
      {/if}
    </footer>
  </form>
</div>
