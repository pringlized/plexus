"""Library-owned logging setup.

Every pinch, batch, and action logged under the `plexus.*` namespace
lands in a single file managed by the library — not by the caller. Drop
Plexus into any project and the central audit log writes itself.

Called from PlexusHub.__init__; idempotent so creating multiple hubs or
re-importing doesn't stack handlers.
"""
import logging
from pathlib import Path

from plexus import config

_FORMAT = "%(asctime)s | %(name)s | %(message)s"


def configure_logging() -> None:
    plexus_logger = logging.getLogger(config.LOGGER_NAME)
    plexus_logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))

    if not config.LOG_FILE:
        return

    target = Path(config.LOG_FILE).resolve()

    # Skip if an equivalent file handler is already attached.
    for h in plexus_logger.handlers:
        if isinstance(h, logging.FileHandler):
            try:
                if Path(h.baseFilename).resolve() == target:
                    return
            except (ValueError, OSError):
                continue

    target.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(target, encoding="utf-8")
    handler.setFormatter(logging.Formatter(_FORMAT))
    plexus_logger.addHandler(handler)
