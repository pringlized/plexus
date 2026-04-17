import type { SignalEvent } from '$lib/types';

// Module-level subscriber registry. Shared by the POST route (which fans
// events out) and the SSE route (which registers browser connections).
//
// Lives on the server only. Fine for local dev / single-process prod.

type Subscriber = (event: SignalEvent) => void;

const subscribers = new Set<Subscriber>();

export function addSubscriber(fn: Subscriber): () => void {
  subscribers.add(fn);
  return () => subscribers.delete(fn);
}

export function broadcast(event: SignalEvent): void {
  for (const fn of subscribers) {
    try {
      fn(event);
    } catch {
      // A faulty subscriber shouldn't break broadcast fan-out.
    }
  }
}
