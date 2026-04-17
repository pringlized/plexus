import time
import random
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plexus import PlexusHub, Severity
from harness.fake_system import (
    FakeSecurityScanner,
    FakeIngestionPipeline,
    FakeBuildEngine,
    FakeAgentWorker,
    FakeHealthMonitor,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("plexus-harness.log"),
    ],
)

log = logging.getLogger("harness")


def main():
    hub = PlexusHub(
        nodes_path="plexus-nodes.yaml",
        receptors_path="plexus-receptors.yaml",
    )

    components = [
        FakeSecurityScanner(),
        FakeIngestionPipeline(),
        FakeBuildEngine(),
        FakeAgentWorker(),
        FakeHealthMonitor(),
    ]

    log.info("Plexus harness started. Firing pinches...")

    iteration = 0
    while True:
        iteration += 1
        component = random.choice(components)
        severity, category, payload = component.random_message()

        hub.pinch(
            component.NODE_ID,
            payload,
            severity=severity,
            category=category,
        )

        delay = random.uniform(0.2, 1.5)
        time.sleep(delay)


if __name__ == "__main__":
    main()
