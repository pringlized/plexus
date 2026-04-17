import yaml from 'js-yaml';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import type { NodeConfig, ReceptorConfig } from '$lib/types';

export const prerender = false;

export async function load() {
  const nodesRaw = readFileSync(resolve('../plexus-nodes.yaml'), 'utf-8');
  const receptorsRaw = readFileSync(resolve('../plexus-receptors.yaml'), 'utf-8');

  const nodesConfig = yaml.load(nodesRaw) as { nodes: Record<string, NodeConfig> };
  const receptorsConfig = yaml.load(receptorsRaw) as { receptors: Record<string, ReceptorConfig> };

  return {
    nodes: nodesConfig.nodes,
    receptors: receptorsConfig.receptors
  };
}
