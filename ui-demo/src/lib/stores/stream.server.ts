// Server-only signal bus. The POST endpoint broadcasts to subscribers
// (open SSE connections). Module-level Set is fine for single-process dev.
import type { SignalEvent } from '$lib/types';

type Subscriber = (event: SignalEvent) => void;

const subscribers = new Set<Subscriber>();

export function addSubscriber(fn: Subscriber): () => void {
  subscribers.add(fn);
  return () => subscribers.delete(fn);
}

export function broadcastSignal(event: SignalEvent): void {
  for (const fn of subscribers) {
    try {
      fn(event);
    } catch {
      // a faulty subscriber must not break broadcast fan-out
    }
  }
}
