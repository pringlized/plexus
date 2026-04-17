from plexus.receptors.base import BaseReceptor
from plexus.models import Signal, ReceptorResult
import logging

log = logging.getLogger("plexus.logger_receptor")


class LoggerReceptor(BaseReceptor):
    def receive(self, signal: Signal) -> ReceptorResult:
        log.debug(
            f"LOG | {signal.node_short_id} | {signal.category} | "
            f"{signal.severity.value} | {signal.payload}"
        )
        return self._discard(signal)
