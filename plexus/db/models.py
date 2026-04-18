"""SQLAlchemy ORM models for Plexus persistence.

Three tables:
  - plexus_nodes          — the logbook of every unique pinch location
  - plexus_action_log     — full audit trail of every action execution
  - plexus_topology_views — saved custom canvas layouts

Cross-database friendly. Uses SQLAlchemy's portable Uuid + JSON types so
the same models work against Postgres, SQLite, and others.
"""
import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class PlexusNode(Base):
    """One row per unique call site that has ever pinched. Updated on
    every signal. Self-prunable via TTL (rev3 maintenance job)."""

    __tablename__ = "plexus_nodes"

    pinch_id = Column(String(12), primary_key=True)
    name = Column(Text, nullable=True)
    layer = Column(Text, nullable=True)
    source_file = Column(Text, nullable=False)
    source_function = Column(Text, nullable=False)
    source_line = Column(Integer, nullable=False)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    ttl_days = Column(Integer, default=90)

    def __repr__(self) -> str:
        return f"<PlexusNode {self.pinch_id} name={self.name}>"


class PlexusActionLog(Base):
    """One row per action execution. A batch fan-out produces N rows
    (one per action), not one per batch."""

    __tablename__ = "plexus_action_log"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pinch_id = Column(String(12), nullable=False, index=True)
    signal_id = Column(Uuid(as_uuid=True), nullable=False)
    action_name = Column(Text, nullable=False, index=True)
    batch_name = Column(Text, nullable=True)
    payload = Column(JSON, nullable=False)
    severity = Column(Text, nullable=False)
    layer = Column(Text, nullable=True)
    node_name = Column(Text, nullable=True)
    source_file = Column(Text, nullable=False)
    source_function = Column(Text, nullable=False)
    source_line = Column(Integer, nullable=False)
    ok = Column(Boolean, nullable=False)
    detail = Column(Text, nullable=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return (
            f"<PlexusActionLog {self.action_name} pinch={self.pinch_id} "
            f"ok={self.ok}>"
        )


class PlexusTopologyView(Base):
    """Saved custom canvas layout. Edges always derived at render time
    from the connection map — only positions are stored."""

    __tablename__ = "plexus_topology_views"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    layout_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<PlexusTopologyView {self.name}>"
