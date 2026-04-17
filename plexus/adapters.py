from plexus.receptors.alerter import AlerterReceptor
from plexus.receptors.health import HealthAggregatorReceptor
from plexus.receptors.logger import LoggerReceptor

RECEPTOR_REGISTRY = {
    "alerter": AlerterReceptor,
    "health_aggregator": HealthAggregatorReceptor,
    "logger": LoggerReceptor,
}


def get_receptor_class(type_str: str):
    cls = RECEPTOR_REGISTRY.get(type_str)
    if not cls:
        raise ValueError(
            f"Unknown receptor type: '{type_str}'. "
            f"Register it in plexus/adapters.py"
        )
    return cls
