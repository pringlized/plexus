import { writable, derived, type Readable } from 'svelte/store';
import type { HealthStatus, SignalEvent } from '$lib/types';

// Ring buffer — keep last 500 events. Newest first.
const MAX_SIGNALS = 500;
const ACTIVE_WINDOW_MS = 10_000;

export const signalEvents = writable<SignalEvent[]>([]);

// Wall-clock tick so derived stores that care about "recent" (10s window)
// naturally re-evaluate as time passes even when no new signals arrive.
export const now = writable(Date.now());
if (typeof window !== 'undefined') {
  setInterval(() => now.set(Date.now()), 1000);
}

export function pushSignal(event: SignalEvent) {
  signalEvents.update((events) => {
    const updated = [event, ...events];
    return updated.slice(0, MAX_SIGNALS);
  });
}

export function clearSignals() {
  signalEvents.set([]);
}

// Signals indexed by node short id.
export const signalsByNode: Readable<Record<string, SignalEvent[]>> = derived(
  signalEvents,
  ($events) => {
    const map: Record<string, SignalEvent[]> = {};
    for (const event of $events) {
      const id = event.signal.node_short_id;
      (map[id] ??= []).push(event);
    }
    return map;
  }
);

// Signals that each receptor received, indexed by receptor id.
export const signalsByReceptor: Readable<Record<string, SignalEvent[]>> = derived(
  signalEvents,
  ($events) => {
    const map: Record<string, SignalEvent[]> = {};
    for (const event of $events) {
      for (const result of event.receptor_results) {
        (map[result.receptor_id] ??= []).push(event);
      }
    }
    return map;
  }
);

// Active anomalies (anomaly/critical severity within the 10s window).
export const activeAnomalies: Readable<number> = derived(
  [signalEvents, now],
  ([$events, $now]) => {
    const cutoff = $now - ACTIVE_WINDOW_MS;
    return $events.filter(
      (e) =>
        (e.signal.severity === 'anomaly' || e.signal.severity === 'critical') &&
        new Date(e.signal.timestamp).getTime() > cutoff
    ).length;
  }
);

// Health per layer, derived from recent signals. Recovers to healthy
// automatically once 10s pass with no fresh non-healthy traffic.
export const layerHealth: Readable<Record<string, HealthStatus>> = derived(
  [signalEvents, now],
  ([$events, $now]) => {
    const cutoff = $now - ACTIVE_WINDOW_MS;
    const recent = $events.filter((e) => new Date(e.signal.timestamp).getTime() > cutoff);

    const health: Record<string, HealthStatus> = {};
    for (const event of recent) {
      const layer = event.signal.node_layer;
      const sev = event.signal.severity;
      const current = health[layer] ?? 'healthy';
      if (sev === 'critical') health[layer] = 'critical';
      else if (sev === 'anomaly' && current !== 'critical') health[layer] = 'anomaly';
      else if (sev === 'warning' && current !== 'critical' && current !== 'anomaly')
        health[layer] = 'warning';
    }
    return health;
  }
);

// Health per node — same logic, keyed by node short id.
export const nodeHealth: Readable<Record<string, HealthStatus>> = derived(
  [signalEvents, now],
  ([$events, $now]) => {
    const cutoff = $now - ACTIVE_WINDOW_MS;
    const recent = $events.filter((e) => new Date(e.signal.timestamp).getTime() > cutoff);

    const health: Record<string, HealthStatus> = {};
    for (const event of recent) {
      const node = event.signal.node_short_id;
      const sev = event.signal.severity;
      const current = health[node] ?? 'healthy';
      if (sev === 'critical') health[node] = 'critical';
      else if (sev === 'anomaly' && current !== 'critical') health[node] = 'anomaly';
      else if (sev === 'warning' && current !== 'critical' && current !== 'anomaly')
        health[node] = 'warning';
    }
    return health;
  }
);
