<script lang="ts">
  import { ArrowLeft, CheckCircle2, X, Layers, Zap } from 'lucide-svelte';
  import { page } from '$app/stores';
  import SeverityBadge from '$lib/components/SeverityBadge.svelte';
  import JsonToggle from '$lib/components/JsonToggle.svelte';
  import { actionEvents, now } from '$lib/stores/signals';
  import { basename, relativeTime, shortHash } from '$lib/util';

  let { data } = $props();

  const name = $derived($page.params.name);
  const batch = $derived(data.batches.find((b) => b.name === name));
  const myEvents = $derived($actionEvents.filter((e) => e.action_result?.batch === name));
  const successful = $derived(myEvents.filter((e) => e.action_result?.ok).length);
  const failed = $derived(myEvents.length - successful);
</script>

{#if !batch}
  <div class="p-6 text-sm text-muted">Batch not found in <code>plexus-actions.yaml</code>.</div>
{:else}
  <div class="flex flex-col gap-4 p-6">
    <header class="card px-5 py-4">
      <div class="mb-1 flex items-center gap-2 text-xs text-muted">
        <a href="/" class="inline-flex items-center gap-1 hover:text-accent"><ArrowLeft size={12} /> Dashboard</a>
      </div>
      <div class="flex items-center gap-3">
        <Layers size={18} class="text-accent" />
        <h1 class="text-xl font-semibold">{batch.name}</h1>
        <span class="chip bg-surface-2 text-muted">{batch.actions.length} actions</span>
      </div>
      <div class="mt-1 mono text-[12px] text-muted">batch · fan-out</div>
    </header>

    <section class="card px-5 py-4">
      <div class="mb-2 text-sm font-medium">Actions in this batch</div>
      <div class="flex flex-wrap gap-2">
        {#each batch.actions as actionName}
          <a href={`/actions/${actionName}`} class="chip bg-surface-2 text-muted hover:text-accent">
            <Zap size={11} class="inline" />
            {actionName}
          </a>
        {/each}
      </div>
    </section>

    <section class="grid grid-cols-2 gap-4 md:grid-cols-4">
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Executions</div>
        <div class="mt-1 text-2xl font-semibold tabular-nums">{myEvents.length}</div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Successful</div>
        <div class="mt-1 text-2xl font-semibold tabular-nums text-sev-healthy">{successful}</div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Failed</div>
        <div class="mt-1 text-2xl font-semibold tabular-nums {failed > 0 ? 'text-sev-critical' : 'text-muted'}">{failed}</div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Last fired</div>
        <div class="mt-1 text-sm">{myEvents[0] ? relativeTime(myEvents[0].received_at, $now) : '—'}</div>
      </div>
    </section>

    <section class="card">
      <div class="border-b border-border px-4 py-2 text-sm font-medium">Recent executions</div>
      <div class="max-h-[500px] overflow-y-auto">
        {#each myEvents.slice(0, 80) as e (e.received_at)}
          <div class="border-b border-border/60 px-4 py-2 text-sm">
            <div class="flex items-center gap-2">
              <SeverityBadge severity={e.severity} size="sm" />
              <span class="text-xs text-muted">{relativeTime(e.received_at, $now)}</span>
              <a href={`/nodes/${e.pinch_id}`} class="font-medium hover:text-accent">
                {e.name ?? shortHash(e.pinch_id)}
              </a>
              <span class="ml-auto">
                {#if e.action_result?.ok}
                  <CheckCircle2 size={12} class="text-sev-healthy" />
                {:else}
                  <X size={12} class="text-sev-critical" />
                {/if}
              </span>
            </div>
            <div class="mono mt-0.5 text-[11px] text-muted">
              {basename(e.source_file)}:{e.source_line} · {e.source_function}
            </div>
            <div class="mono mt-0.5 text-[10.5px] text-muted/80">
              fired: {e.action_result?.actions_fired.join(', ')}
            </div>
            {#if e.action_result?.detail}
              <div class="mono mt-0.5 text-[10.5px] text-sev-critical/80">{e.action_result.detail}</div>
            {/if}
            <JsonToggle data={e} label="Signal JSON" />
          </div>
        {/each}
        {#if myEvents.length === 0}
          <div class="p-6 text-center text-xs text-muted">No executions yet.</div>
        {/if}
      </div>
    </section>
  </div>
{/if}
