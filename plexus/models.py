from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone


class Severity(str, Enum):
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ANOMALY = "anomaly"
    CRITICAL = "critical"


# ---- Configuration -----------------------------------------------------


class ActionConfig(BaseModel):
    """One entry under `actions:` in plexus-actions.yaml.

    Minimal on purpose. The action name IS the adapter — no type
    indirection. Per-adapter config (credentials, channels, recipients)
    lives wherever the adapter decides to read it from.
    """
    enabled: bool = True


class BatchConfig(BaseModel):
    """One entry under `batches:` — ordered list of action names."""
    actions: list[str]


class PlexusConfig(BaseModel):
    actions: dict[str, ActionConfig] = Field(default_factory=dict)
    batches: dict[str, BatchConfig] = Field(default_factory=dict)


# ---- Signal envelope ---------------------------------------------------


class Signal(BaseModel):
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # Stable sha256[:12] of source_file:source_function:source_line.
    pinch_id: str
    # Optional human label — UI shows this instead of the hash when set.
    name: str | None = None
    source_file: str
    source_line: int
    source_function: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: Severity
    layer: str | None = None
    payload: dict[str, Any]
    sequence: int


# ---- Action result / wire envelope -------------------------------------


class ActionResult(BaseModel):
    """Per-action outcome returned by BaseAction.execute(). Internal."""
    action_id: str
    signal_id: str
    ok: bool
    detail: str | None = None
    logged_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---- Wire contract (flat) — what the UI receives over POST ------------


class WireActionResult(BaseModel):
    """Rolled-up outcome for whatever the pinch's `action` param resolved
    to (single action or batch). One bool, one list of names that fired."""
    batch: str | None = None      # batch name if `action` resolved to a batch
    actions_fired: list[str]      # action names that actually executed
    ok: bool                       # all() across constituent actions
    detail: str | None = None      # joined failure details if any


class WireEvent(BaseModel):
    """Flat envelope POSTed to the UI. Spec source-of-truth shape."""
    pinch_id: str
    name: str | None = None
    layer: str | None = None
    severity: Severity
    source_file: str
    source_line: int
    source_function: str
    payload: dict[str, Any]
    timestamp: datetime
    action: str | None = None
    action_result: WireActionResult | None = None
