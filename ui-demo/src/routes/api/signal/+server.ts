import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import type { SignalEvent } from '$lib/types';
import { broadcast } from '$lib/server/signal-bus';

export const POST: RequestHandler = async ({ request }) => {
  try {
    const body = await request.json();

    const event: SignalEvent = {
      signal: body.signal,
      receptor_results: body.receptor_results ?? [],
      received_at: Date.now()
    };

    broadcast(event);
    return json({ ok: true });
  } catch {
    // Never let a bad payload crash the server.
    return json({ ok: false }, { status: 400 });
  }
};
