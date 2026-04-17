<script lang="ts">
  import { page } from '$app/stores';
  import { LayoutDashboard, Network, Radio, Cpu, Radar } from 'lucide-svelte';
  import { nodes, receptors } from '$lib/sim/store.svelte';

  const primary = [
    { href: '/', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/topology', label: 'Topology', icon: Network },
    { href: '/monitor', label: 'Monitor', icon: Radio }
  ];

  function isActive(href: string, pathname: string) {
    if (href === '/') return pathname === '/';
    return pathname === href || pathname.startsWith(href + '/');
  }
</script>

<aside class="flex h-full w-60 shrink-0 flex-col border-r border-border bg-surface">
  <div class="flex items-center gap-2 px-4 py-4">
    <svg viewBox="0 0 24 24" class="h-6 w-6 text-accent" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 2 L22 7.5 V16.5 L12 22 L2 16.5 V7.5 Z" />
      <circle cx="12" cy="12" r="2.5" fill="currentColor" />
    </svg>
    <div class="flex flex-col leading-tight">
      <span class="text-sm font-semibold tracking-wider">PLEXUS</span>
      <span class="text-[10px] uppercase tracking-widest text-muted">Signal Nervous System</span>
    </div>
  </div>

  <nav class="flex-1 overflow-y-auto px-2 pb-4">
    <ul class="space-y-0.5">
      {#each primary as item}
        {@const active = isActive(item.href, $page.url.pathname)}
        <li>
          <a
            href={item.href}
            class="flex items-center gap-2 rounded-md px-3 py-2 text-sm transition
              {active ? 'bg-surface-2 text-text' : 'text-muted hover:bg-surface-2 hover:text-text'}"
          >
            <item.icon size={15} />
            {item.label}
          </a>
        </li>
      {/each}
    </ul>

    <div class="mt-5 px-3 text-[10px] uppercase tracking-widest text-muted">Nodes</div>
    <ul class="mt-1 space-y-0.5">
      {#each nodes as n}
        {@const href = `/nodes/${n.id}`}
        {@const active = isActive(href, $page.url.pathname)}
        <li>
          <a
            {href}
            class="flex items-center gap-2 rounded-md px-3 py-1.5 text-[12.5px] transition
              {active ? 'bg-surface-2 text-text' : 'text-muted hover:bg-surface-2 hover:text-text'}"
          >
            <Cpu size={13} class="opacity-70" />
            <span class="truncate">{n.name}</span>
          </a>
        </li>
      {/each}
    </ul>

    <div class="mt-5 px-3 text-[10px] uppercase tracking-widest text-muted">Receptors</div>
    <ul class="mt-1 space-y-0.5">
      {#each receptors as r}
        {@const href = `/receptors/${r.id}`}
        {@const active = isActive(href, $page.url.pathname)}
        <li>
          <a
            {href}
            class="flex items-center gap-2 rounded-md px-3 py-1.5 text-[12.5px] transition
              {active ? 'bg-surface-2 text-text' : 'text-muted hover:bg-surface-2 hover:text-text'}"
          >
            <Radar size={13} class="opacity-70" />
            <span class="truncate">{r.name}</span>
          </a>
        </li>
      {/each}
    </ul>
  </nav>
</aside>
