import yaml from 'js-yaml';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import type { ActionConfig, BatchConfig } from '$lib/types';

export const prerender = false;

interface RawConfig {
  actions?: Record<string, { enabled?: boolean; [k: string]: unknown }>;
  batches?: Record<string, string[]>;
}

export async function load() {
  const raw = readFileSync(resolve('../plexus-actions.yaml'), 'utf-8');
  const cfg = (yaml.load(raw) ?? {}) as RawConfig;

  const actions: ActionConfig[] = Object.entries(cfg.actions ?? {}).map(
    ([name, body]) => ({
      name,
      enabled: body?.enabled ?? true,
      ...body
    })
  );

  const batches: BatchConfig[] = Object.entries(cfg.batches ?? {}).map(
    ([name, actionList]) => ({
      name,
      actions: actionList ?? []
    })
  );

  return { actions, batches };
}
