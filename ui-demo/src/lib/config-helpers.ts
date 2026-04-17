import type { NodeConfig, ReceptorConfig, LayerSummary } from './types';

const LAYER_DESCRIPTIONS: Record<string, string> = {
  security: 'Character & pattern threat detection',
  ingestion: 'Knowledge pipeline events',
  build: 'Build chain & pipeline state',
  agent: 'Agent task lifecycle',
  health: 'System health & heartbeat',
  pipeline: 'Workflow state transitions'
};

const LAYER_ORDER = ['security', 'ingestion', 'build', 'agent', 'health', 'pipeline'];

export function deriveLayers(nodes: Record<string, NodeConfig>): LayerSummary[] {
  const layerMap: Record<string, LayerSummary> = {};

  for (const [shortId, node] of Object.entries(nodes)) {
    if (!layerMap[node.layer]) {
      layerMap[node.layer] = {
        name: node.layer,
        description: LAYER_DESCRIPTIONS[node.layer] ?? '',
        nodes: []
      };
    }
    layerMap[node.layer].nodes.push({ shortId, config: node });
  }

  return Object.values(layerMap).sort((a, b) => {
    const ai = LAYER_ORDER.indexOf(a.name);
    const bi = LAYER_ORDER.indexOf(b.name);
    if (ai === -1 && bi === -1) return a.name.localeCompare(b.name);
    if (ai === -1) return 1;
    if (bi === -1) return -1;
    return ai - bi;
  });
}

export function receptorsFor(
  nodeShortId: string,
  receptors: Record<string, ReceptorConfig>
): Array<{ id: string; config: ReceptorConfig }> {
  return Object.entries(receptors)
    .filter(([, r]) => r.listens_to.includes(nodeShortId))
    .map(([id, config]) => ({ id, config }));
}

export function layerDescription(layer: string): string {
  return LAYER_DESCRIPTIONS[layer] ?? '';
}
