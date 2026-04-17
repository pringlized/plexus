import { error } from '@sveltejs/kit';

export async function load({ params, parent }) {
  const { nodes, receptors } = await parent();
  const receptor = receptors[params.receptorId];

  if (!receptor) {
    throw error(404, `Receptor '${params.receptorId}' not found`);
  }

  const listenedNodes = receptor.listens_to.map((nodeId) => ({
    id: nodeId,
    config: nodes[nodeId] ?? null
  }));

  return {
    receptorId: params.receptorId,
    receptor,
    listenedNodes
  };
}
