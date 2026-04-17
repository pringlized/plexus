import { error } from '@sveltejs/kit';

export async function load({ params, parent }) {
  const { nodes, receptors } = await parent();
  const node = nodes[params.shortId];

  if (!node) {
    throw error(404, `Node '${params.shortId}' not found`);
  }

  const wiredReceptors = Object.entries(receptors)
    .filter(([, r]) => r.listens_to.includes(params.shortId))
    .map(([id, r]) => ({ id, ...r }));

  return {
    shortId: params.shortId,
    node,
    wiredReceptors
  };
}
