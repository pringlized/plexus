from plexus.receptors.base import BaseReceptor
from plexus.models import Signal, ReceptorResult, Severity


class HealthAggregatorReceptor(BaseReceptor):
    def receive(self, signal: Signal) -> ReceptorResult:
        severity_filter = [
            Severity(s) for s in self.config.config.get("severity_filter", [])
        ]
        if signal.severity not in severity_filter:
            return self._discard(signal)

        if signal.severity in (Severity.ANOMALY, Severity.CRITICAL):
            reason = (
                f"Health degraded: {signal.node_description} "
                f"reported {signal.severity.value}"
            )
            return self._flag(signal, reason)

        return self._discard(signal)
