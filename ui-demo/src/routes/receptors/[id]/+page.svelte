<script lang="ts">
  import { page } from '$app/stores';
  import { ArrowLeft, Zap, CheckCircle2, Loader2 } from 'lucide-svelte';
  import { receptors, receiptsByReceptor, actionsByReceptor, nodes, sim } from '$lib/sim/store.svelte';
  import { relativeTime } from '$lib/util';
  import SeverityBadge from '$lib/components/SeverityBadge.svelte';

  const receptorId = $derived($page.params.id);
  const receptor = $derived(receptors.find((r) => r.id === receptorId));
  const receipts = $derived(receptor ? receiptsByReceptor(receptor.id, 80) : []);
  const actions = $derived(receptor ? actionsByReceptor(receptor.id, 50) : []);
  const invocationsToday = $derived(actions.length);
  const successful = $derived(actions.filter((a) => a.status === 'completed').length);
  const avgMs = $derived(() => {
    const withDur = actions.filter((a) => a.duration_ms != null);
    if (!withDur.length) return 0;
    return Math.round(withDur.reduce((acc, a) => acc + (a.duration_ms || 0), 0) / withDur.length);
  });

  function nodeName(id: string) {
    return nodes.find((n) => n.id === id)?.name ?? id;
  }
</script>

{#if !receptor}
  <div class="p-6 text-sm text-muted">Receptor not found.</div>
{:else}
  <div class="flex flex-col gap-4 p-6">
    <header class="card px-5 py-4">
      <div class="mb-1 flex items-center gap-2 text-xs text-muted">
        <a href="/" class="inline-flex items-center gap-1 hover:text-accent"><ArrowLeft size={12} /> Back</a>
      </div>
      <div class="flex items-center gap-3">
        <h1 class="text-xl font-semibold">{receptor.name}</h1>
        <span class="chip bg-sev-healthy/15 text-sev-healthy">ACTIVE</span>
      </div>
      <div class="mt-1 mono text-[12px] text-muted">{receptor.type} · {receptor.id}</div>
      <p class="mt-2 text-sm text-muted">{receptor.description}</p>
    </header>

    <section class="card px-5 py-4">
      <div class="mb-2 text-sm font-medium">Configuration</div>
      <div class="grid grid-cols-1 gap-2 text-sm md:grid-cols-3">
        <div><span class="text-muted">Listens to:</span> {receptor.listensTo === '*' ? 'all nodes' : receptor.listensTo.map(nodeName).join(', ')}</div>
        <div><span class="text-muted">Fires on:</span> {receptor.firesOn === '*' ? 'all severities' : receptor.firesOn.join(', ')}</div>
        <div><span class="text-muted">Action:</span> {receptor.action ?? 'none'}</div>
      </div>
    </section>

    <section class="grid grid-cols-2 gap-4 md:grid-cols-4">
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Invocations</div>
        <div class="mt-1 text-2xl font-semibold tabular-nums">{invocationsToday}</div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Successful</div>
        <div class="mt-1 text-2xl font-semibold tabular-nums text-sev-healthy">{successful}</div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Receipts</div>
        <div class="mt-1 text-2xl font-semibold tabular-nums">{receipts.length}</div>
      </div>
      <div class="card px-4 py-3">
        <div class="text-xs text-muted">Avg response</div>
        <div class="mt-1 text-sm">{avgMs() ? `${avgMs()}ms` : '—'}</div>
      </div>
    </section>

    {#if actions.length > 0}
      <section class="card">
        <div class="border-b border-border px-4 py-2 text-sm font-medium">Recent actions</div>
        <div class="max-h-[420px] overflow-y-auto">
          {#each actions as a (a.id)}
            <div class="border-b border-border/60 px-4 py-2.5 text-sm">
              <div class="flex items-center gap-2">
                <Zap size={13} class="text-accent" />
                <span class="font-medium">{a.action}</span>
                <span class="text-xs text-muted">{relativeTime(a.timestamp, sim.now)}</span>
                <span class="ml-auto">
                  {#if a.status === 'pending'}
                    <Loader2 size={12} class="animate-spin text-muted" />
                  {:else if a.status === 'completed'}
                    <CheckCircle2 size={12} class="text-sev-healthy" />
                  {/if}
                </span>
              </div>
              <div class="mono mt-1 text-[11px] text-muted">{a.detail}</div>
              <div class="mono mt-0.5 text-[10px] text-muted">Node: {nodeName(a.node_id)} · {a.duration_ms ? `${a.duration_ms}ms` : 'pending'}</div>
            </div>
          {/each}
        </div>
      </section>
    {/if}

    <section class="card">
      <div class="border-b border-border px-4 py-2 text-sm font-medium">Recent receipts</div>
      <div class="max-h-[420px] overflow-y-auto">
        {#each receipts as r (r.id)}
          <div class="border-b border-border/60 px-4 py-2 text-sm">
            <div class="flex items-center gap-2">
              <SeverityBadge severity={r.severity} size="sm" />
              <span class="text-xs text-muted">{relativeTime(r.timestamp, sim.now)}</span>
              <span>from <a href={`/nodes/${r.node_id}`} class="hover:text-accent">{nodeName(r.node_id)}</a></span>
              <span class="ml-auto text-[11px] text-sev-healthy">✓</span>
            </div>
            <div class="mono mt-0.5 text-[11px] text-muted">{r.summary}</div>
          </div>
        {/each}
        {#if receipts.length === 0}
          <div class="p-6 text-center text-xs text-muted">No receipts yet.</div>
        {/if}
      </div>
    </section>
  </div>
{/if}
