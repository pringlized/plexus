import { pushSignal } from './signals';
import type { SignalEvent } from '$lib/types';

let eventSource: EventSource | null = null;

export function startStream() {
  if (typeof window === 'undefined') return;
  if (eventSource) return; // already connected

  eventSource = new EventSource('/api/stream');

  eventSource.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      if (data.type === 'signal') {
        pushSignal(data.payload as SignalEvent);
      }
    } catch {
      // Malformed event — ignore.
    }
  };

  eventSource.onerror = () => {
    // Browser auto-reconnects per SSE spec. Nothing to do here.
  };
}

export function stopStream() {
  eventSource?.close();
  eventSource = null;
}
