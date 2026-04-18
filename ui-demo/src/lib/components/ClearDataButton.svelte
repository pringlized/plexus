<script lang="ts">
  import { Trash2 } from 'lucide-svelte';
  import { clearSignals } from '$lib/stores/signals';

  function onClick() {
    if (confirm('Clear all live signals, nodes, and observed connections from the browser?')) {
      clearSignals();
    }
  }
</script>

<button
  type="button"
  onclick={onClick}
  class="inline-flex h-8 items-center gap-1.5 rounded-md border border-border bg-surface px-2.5 text-xs font-medium text-muted transition hover:border-sev-critical/50 hover:text-sev-critical"
  aria-label="Clear browser data"
  title="Clear all signals, nodes, and observed connections from this browser session"
>
  <Trash2 size={13} />
  Clear Data
</button>
