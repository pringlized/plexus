import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getDb } from '$lib/server/db';

interface ViewFull {
  id: string;
  name: string;
  description: string | null;
  layout_json: string;
  created_at: string;
  updated_at: string;
}

// GET /api/views/[id] — fetch one view with parsed layout_json.
export const GET: RequestHandler = ({ params }) => {
  const db = getDb();
  const row = db
    .prepare('SELECT * FROM plexus_topology_views WHERE id = ?')
    .get(params.id) as ViewFull | undefined;

  if (!row) throw error(404, `View '${params.id}' not found`);

  return json({
    ...row,
    layout_json: JSON.parse(row.layout_json)
  });
};

// PUT /api/views/[id] — update layout (and optionally name/description).
export const PUT: RequestHandler = async ({ params, request }) => {
  const body = await request.json();
  const { layout_json, name, description } = body ?? {};
  const now = new Date().toISOString();

  const db = getDb();
  const existing = db
    .prepare('SELECT id FROM plexus_topology_views WHERE id = ?')
    .get(params.id);

  if (!existing) throw error(404, `View '${params.id}' not found`);

  db.prepare(
    `UPDATE plexus_topology_views
        SET layout_json = ?,
            name        = COALESCE(?, name),
            description = COALESCE(?, description),
            updated_at  = ?
      WHERE id = ?`
  ).run(
    JSON.stringify(layout_json),
    name ?? null,
    description ?? null,
    now,
    params.id
  );

  return json({ ok: true, updated_at: now });
};

// DELETE /api/views/[id] — remove a saved view.
export const DELETE: RequestHandler = ({ params }) => {
  const db = getDb();
  const result = db
    .prepare('DELETE FROM plexus_topology_views WHERE id = ?')
    .run(params.id);

  if (result.changes === 0) throw error(404, `View '${params.id}' not found`);
  return json({ ok: true });
};
