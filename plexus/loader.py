import yaml
from plexus.models import PlexusConfig, NodeConfig, ReceptorConfig


def load_config(nodes_path: str, receptors_path: str) -> PlexusConfig:
    with open(nodes_path) as f:
        nodes_raw = yaml.safe_load(f)

    with open(receptors_path) as f:
        receptors_raw = yaml.safe_load(f)

    nodes = {
        k: NodeConfig(**v)
        for k, v in nodes_raw.get("nodes", {}).items()
    }

    receptors = {
        k: ReceptorConfig(**v)
        for k, v in receptors_raw.get("receptors", {}).items()
    }

    return PlexusConfig(nodes=nodes, receptors=receptors)
