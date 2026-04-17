from plexus.receptors.base import BaseReceptor
from plexus.models import Signal, ReceptorResult, Severity


class AlerterReceptor(BaseReceptor):
    def receive(self, signal: Signal) -> ReceptorResult:
        severity_filter = [
            Severity(s) for s in self.config.config.get("severity_filter", [])
        ]
        if signal.severity not in severity_filter:
            return self._discard(signal)

        label = self.config.config.get("alert_label", "ALERT")
        reason = (
            f"{label}: {signal.category} from {signal.node_description} "
            f"[{signal.severity.value.upper()}]"
        )
        return self._flag(signal, reason)
