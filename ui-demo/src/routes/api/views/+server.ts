import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getDb } from '$lib/server/db';

interface ViewRow {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

// GET /api/views — lightweight list (no layout_json payload).
export const GET: RequestHandler = () => {
  const db = getDb();
  const rows = db
    .prepare(
      `SELECT id, name, description, created_at, updated_at
         FROM plexus_topology_views
         ORDER BY updated_at DESC`
    )
    .all() as ViewRow[];
  return json(rows);
};

// POST /api/views — create a new saved view.
export const POST: RequestHandler = async ({ request }) => {
  const body = await request.json();
  const { name, description, layout_json } = body ?? {};

  if (!name || !layout_json) {
    return json(
      { error: 'name and layout_json are required' },
      { status: 400 }
    );
  }

  const id = crypto.randomUUID();
  const now = new Date().toISOString();

  const db = getDb();
  db.prepare(
    `INSERT INTO plexus_topology_views
       (id, name, description, layout_json, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?)`
  ).run(id, name, description ?? null, JSON.stringify(layout_json), now, now);

  return json(
    { id, name, description: description ?? null, created_at: now, updated_at: now },
    { status: 201 }
  );
};
