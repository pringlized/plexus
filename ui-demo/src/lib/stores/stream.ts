import { pushSignal } from './signals';
import type { SignalEvent } from '$lib/types';

let eventSource: EventSource | null = null;

export function startStream(): void {
  if (typeof window === 'undefined') return;
  if (eventSource) return;
  eventSource = new EventSource('/api/stream');
  eventSource.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      if (data.type === 'signal') pushSignal(data.payload as SignalEvent);
    } catch {
      // malformed event — ignore
    }
  };
  eventSource.onerror = () => {
    // browser auto-reconnects per SSE spec
  };
}

export function stopStream(): void {
  eventSource?.close();
  eventSource = null;
}
