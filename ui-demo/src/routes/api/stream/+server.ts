import type { RequestHandler } from './$types';
import { addSubscriber, getRecentEvents } from '$lib/stores/stream.server';

export const GET: RequestHandler = () => {
  let cleanup: (() => void) | null = null;
  let heartbeat: ReturnType<typeof setInterval> | null = null;

  const stream = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder();

      const send = (data: unknown) => {
        try {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
        } catch {
          // client disconnected
        }
      };

      send({ type: 'connected' });

      // Replay the recent ring buffer so a new client (refresh, new tab,
      // SSE auto-reconnect, navigation) catches up to current state.
      for (const event of getRecentEvents()) {
        send({ type: 'signal', payload: event });
      }

      cleanup = addSubscriber((event) => send({ type: 'signal', payload: event }));

      heartbeat = setInterval(() => {
        try {
          controller.enqueue(encoder.encode(`:keepalive\n\n`));
        } catch {
          // ignore
        }
      }, 20_000);
    },
    cancel() {
      cleanup?.();
      if (heartbeat) clearInterval(heartbeat);
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive'
    }
  });
};
