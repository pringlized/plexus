"""Dispatches a build-fixer agent in response to a failed build pinch.

Stand-in adapter — logs only."""
import logging

from plexus import config
from plexus.actions.base import BaseAction
from plexus.models import ActionResult, Signal

log = logging.getLogger(f"{config.LOGGER_NAME}.invoke_build_fixer")


class InvokeBuildFixerAction(BaseAction):
    def execute(self, signal: Signal) -> ActionResult:
        log.info(
            f"invoking build-fixer for signal from {signal.source_function} "
            f"(payload keys: {list(signal.payload.keys())})"
        )
        return self._ok(signal, "build-fixer invoked")
