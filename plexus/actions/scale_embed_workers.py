"""Scales embedding workers up when the ingestion pipeline stalls.

Stand-in adapter — logs only."""
import logging

from plexus import config
from plexus.actions.base import BaseAction
from plexus.models import ActionResult, Signal

log = logging.getLogger(f"{config.LOGGER_NAME}.scale_embed_workers")


class ScaleEmbedWorkersAction(BaseAction):
    def execute(self, signal: Signal) -> ActionResult:
        current = signal.payload.get("worker_count", "?")
        log.info(
            f"scaling embed workers (current={current}) in response to "
            f"{signal.source_function}"
        )
        return self._ok(signal, "embed workers scaled")
