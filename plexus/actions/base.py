from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from plexus.models import ActionResult, Signal

if TYPE_CHECKING:
    from plexus.hub import PlexusHub


class BaseAction(ABC):
    """An action is a single real-world effect triggered by a pinch.

    Adapters read whatever external config they need (channels, creds,
    recipients) on their own — the hub does not manage per-adapter config.
    The hub holds no opinions: it calls execute() with the full signal
    envelope and records the result.
    """

    def __init__(self, action_id: str, hub: "PlexusHub"):
        self.action_id = action_id
        self.hub = hub

    @abstractmethod
    def execute(self, signal: Signal) -> ActionResult:
        """Do the specific thing. Return an ActionResult for the audit log."""
        ...

    def _ok(self, signal: Signal, detail: str | None = None) -> ActionResult:
        return ActionResult(
            action_id=self.action_id,
            signal_id=signal.signal_id,
            ok=True,
            detail=detail,
        )

    def _fail(self, signal: Signal, detail: str) -> ActionResult:
        return ActionResult(
            action_id=self.action_id,
            signal_id=signal.signal_id,
            ok=False,
            detail=detail,
        )
