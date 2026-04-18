"""Sends an ops notification (Slack/email/PagerDuty) for the pinch.

Stand-in adapter — logs only. Replace with a real notifier when the
ops channel wiring lands."""
import logging

from plexus import config
from plexus.actions.base import BaseAction
from plexus.models import ActionResult, Signal

log = logging.getLogger(f"{config.LOGGER_NAME}.notify_ops")


class NotifyOpsAction(BaseAction):
    def execute(self, signal: Signal) -> ActionResult:
        log.info(
            f"notifying ops for {signal.severity.value} signal "
            f"from {signal.source_function} (layer={signal.layer})"
        )
        return self._ok(signal, "ops notified")
