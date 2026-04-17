import yaml

from plexus.models import ActionConfig, BatchConfig, PlexusConfig


def load_config(action_config: str) -> PlexusConfig:
    with open(action_config) as f:
        raw = yaml.safe_load(f) or {}

    actions_raw = raw.get("actions", {}) or {}
    batches_raw = raw.get("batches", {}) or {}

    actions = {
        name: ActionConfig(**body)
        for name, body in actions_raw.items()
    }

    batches = {
        name: BatchConfig(actions=action_list)
        for name, action_list in batches_raw.items()
    }

    return PlexusConfig(actions=actions, batches=batches)
