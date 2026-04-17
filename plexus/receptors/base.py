from abc import ABC, abstractmethod
from plexus.models import Signal, ReceptorResult, ReceptorConfig


class BaseReceptor(ABC):
    def __init__(self, receptor_id: str, config: ReceptorConfig):
        self.receptor_id = receptor_id
        self.config = config

    @abstractmethod
    def receive(self, signal: Signal) -> ReceptorResult:
        """
        Evaluate the signal. Return a ReceptorResult with:
        - action = "discard" → /dev/null
        - action = "flag"    → flagged, logged
        - action = "flag+action" → flagged + action queued (rev2)
        """
        ...

    def _discard(self, signal: Signal) -> ReceptorResult:
        return ReceptorResult(
            receptor_id=self.receptor_id,
            receptor_type=self.config.type,
            signal_id=signal.signal_id,
            action="discard",
        )

    def _flag(self, signal: Signal, reason: str) -> ReceptorResult:
        return ReceptorResult(
            receptor_id=self.receptor_id,
            receptor_type=self.config.type,
            signal_id=signal.signal_id,
            action="flag",
            flag_reason=reason,
        )
