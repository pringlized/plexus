// Server-only signal bus. The POST endpoint pushes events here; the SSE
// endpoint replays the recent buffer to each new client and then streams
// live events. Module-level state is fine for single-process dev.
import type { SignalEvent } from '$lib/types';

type Subscriber = (event: SignalEvent) => void;

const RECENT_BUFFER_SIZE = 500;
const recentEvents: SignalEvent[] = [];
const subscribers = new Set<Subscriber>();

export function addSubscriber(fn: Subscriber): () => void {
  subscribers.add(fn);
  return () => subscribers.delete(fn);
}

/** Snapshot of the recent buffer, oldest first. Safe to iterate. */
export function getRecentEvents(): readonly SignalEvent[] {
  return recentEvents;
}

export function broadcastSignal(event: SignalEvent): void {
  recentEvents.push(event);
  if (recentEvents.length > RECENT_BUFFER_SIZE) {
    recentEvents.shift();
  }
  for (const fn of subscribers) {
    try {
      fn(event);
    } catch {
      // a faulty subscriber must not break broadcast fan-out
    }
  }
}
