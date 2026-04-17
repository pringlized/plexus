import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import type { SignalEvent } from '$lib/types';
import { broadcastSignal } from '$lib/stores/stream.server';

export const POST: RequestHandler = async ({ request }) => {
  try {
    const body = (await request.json()) as Omit<SignalEvent, 'received_at'>;
    const event: SignalEvent = { ...body, received_at: Date.now() };
    broadcastSignal(event);
    return json({ ok: true });
  } catch {
    return json({ ok: false }, { status: 400 });
  }
};
