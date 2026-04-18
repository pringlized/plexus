<script lang="ts">
  import { X } from 'lucide-svelte';

  let {
    initialName = '',
    initialDescription = '',
    saving = false,
    error = null as string | null,
    onsave,
    oncancel
  }: {
    initialName?: string;
    initialDescription?: string;
    saving?: boolean;
    error?: string | null;
    onsave: (v: { name: string; description: string }) => void;
    oncancel: () => void;
  } = $props();

  let name = $state(initialName);
  let description = $state(initialDescription);

  const trimmedName = $derived(name.trim());
  const canSave = $derived(trimmedName.length > 0 && !saving);

  function submit(e: SubmitEvent) {
    e.preventDefault();
    if (!canSave) return;
    onsave({ name: trimmedName, description: description.trim() });
  }

  function onBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) oncancel();
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') oncancel();
  }
</script>

<svelte:window onkeydown={onKey} />

<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="save-view-title"
  onclick={onBackdropClick}
  class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
>
  <form
    onsubmit={submit}
    class="w-full max-w-md rounded-xl border border-border bg-surface shadow-2xl"
  >
    <header class="flex items-start justify-between border-b border-border px-5 py-4">
      <div>
        <h2 id="save-view-title" class="text-base font-semibold">
          {initialName ? 'Update topology view' : 'Save topology view'}
        </h2>
        <p class="mt-0.5 text-xs text-muted">
          Give this canvas a name so you can find it again.
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

    <div class="space-y-4 px-5 py-4">
      <label class="block">
        <span class="block text-xs font-medium text-muted">Name</span>
        <input
          type="text"
          bind:value={name}
          autofocus
          required
          placeholder="e.g. Security incident response"
          class="mt-1 w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text placeholder:text-muted/60 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/40"
        />
      </label>

      <label class="block">
        <span class="block text-xs font-medium text-muted">Description (optional)</span>
        <textarea
          bind:value={description}
          rows="3"
          placeholder="What is this view for?"
          class="mt-1 w-full resize-none rounded-md border border-border bg-bg px-3 py-2 text-sm text-text placeholder:text-muted/60 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent/40"
        ></textarea>
      </label>

      {#if error}
        <p class="text-xs text-sev-critical">{error}</p>
      {/if}
    </div>

    <footer class="flex items-center justify-end gap-2 border-t border-border px-5 py-3">
      <button
        type="button"
        onclick={oncancel}
        disabled={saving}
        class="rounded-md border border-border bg-surface px-3 py-1.5 text-xs text-muted transition hover:text-text disabled:opacity-50"
      >
        Cancel
      </button>
      <button
        type="submit"
        disabled={!canSave}
        class="rounded-md border border-accent bg-accent px-3 py-1.5 text-xs font-medium text-bg transition hover:bg-accent/90 disabled:opacity-50"
      >
        {saving ? 'Saving…' : 'Save'}
      </button>
    </footer>
  </form>
</div>
