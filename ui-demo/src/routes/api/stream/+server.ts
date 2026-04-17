import type { RequestHandler } from './$types';
import { addSubscriber } from '$lib/server/signal-bus';

export const GET: RequestHandler = () => {
  let cleanup: (() => void) | null = null;
  let heartbeat: ReturnType<typeof setInterval> | null = null;

  const stream = new ReadableStream({
    start(controller) {
      const encoder = new TextEncoder();

      const send = (payload: unknown) => {
        try {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(payload)}\n\n`));
        } catch {
          // Client disconnected; cancel() will fire.
        }
      };

      // Initial ping so the browser knows it's connected.
      send({ type: 'connected' });

      cleanup = addSubscriber((event) => {
        send({ type: 'signal', payload: event });
      });

      // Periodic keep-alive comment to prevent idle proxies from closing.
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
