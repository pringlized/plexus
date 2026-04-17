import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plexus import PlexusHub
from harness.fake_system import fire_random


def main() -> None:
    hub = PlexusHub()
    while True:
        fire_random(hub)
        time.sleep(random.uniform(0.2, 1.5))


if __name__ == "__main__":
    main()
