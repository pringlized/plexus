// Singleton SQLite connection shared by all SvelteKit API routes.
//
// WAL mode is the load-bearing pragma — it lets the Python hub keep
// writing signal/action rows while SvelteKit reads (and occasionally
// writes) topology view rows, without lock contention. Without it the
// two sides will deadlock on the file under any real traffic.
import Database from 'better-sqlite3';
import { env } from '$env/dynamic/private';
import path from 'path';

let _db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (_db) return _db;

  const dbPath = path.resolve(env.PLEXUS_DB_PATH ?? '../data/plexus.db');
  _db = new Database(dbPath);
  _db.pragma('journal_mode = WAL');
  _db.pragma('foreign_keys = ON');
  return _db;
}
