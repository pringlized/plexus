"""First real action — dispatches the security responder callable with
the full signal envelope. This is the 'first truck leaving the building'."""
import logging

from plexus import config
from plexus.actions.base import BaseAction
from plexus.models import ActionResult, Signal

log = logging.getLogger(f"{config.LOGGER_NAME}.security_agent")


class SecurityAgentAction(BaseAction):
    def execute(self, signal: Signal) -> ActionResult:
        # Import lazily so the library doesn't require the agents/
        # package to exist for projects that don't wire this action.
        try:
            from agents.security_responder import handle
        except ImportError as e:
            return self._fail(signal, f"agents.security_responder not importable: {e}")

        log.info(
            f"dispatching security responder for signal {signal.signal_id} "
            f"(pinch {signal.pinch_id}, from {signal.source_function})"
        )
        try:
            handle(signal, self.hub)
        except Exception as e:
            log.exception(f"security responder raised: {e}")
            return self._fail(signal, f"responder raised: {e}")

        return self._ok(signal, "security responder dispatched")
