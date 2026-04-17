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


class NodeType(str, Enum):
    SECURITY = "security"
    INGESTION = "ingestion"
    BUILD = "build"
    AGENT = "agent"
    HEALTH = "health"
    PIPELINE = "pipeline"


class NodeConfig(BaseModel):
    uuid: str
    type: NodeType
    layer: str
    description: str


class ReceptorConfig(BaseModel):
    uuid: str
    type: str
    description: str
    listens_to: list[str]
    config: dict[str, Any] = Field(default_factory=dict)


class PlexusConfig(BaseModel):
    nodes: dict[str, NodeConfig]
    receptors: dict[str, ReceptorConfig]


class Signal(BaseModel):
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    node_short_id: str
    node_uuid: str
    node_type: NodeType
    node_layer: str
    node_description: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: Severity
    category: str
    payload: dict[str, Any]
    sequence: int
    # Call site — captured automatically by hub.pinch()
    source_file: str | None = None
    source_line: int | None = None
    source_function: str | None = None


class ReceptorResult(BaseModel):
    receptor_id: str
    receptor_type: str
    signal_id: str
    action: str            # "discard" | "flag" | "flag+action"
    flag_reason: str | None = None
    logged_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
