"""All database operations live here. Hub calls these methods; no SQL or
SQLAlchemy code anywhere else in the library."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from plexus import config
from plexus.db.models import (
    Base,
    PlexusActionLog,
    PlexusNode,
    PlexusTopologyView,
)
from plexus.models import Signal

log = logging.getLogger(f"{config.LOGGER_NAME}.db")


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PlexusDB:
    """Thin DB wrapper. Owned by PlexusHub. Never raises into the hub —
    write failures log and swallow so persistence issues don't take down
    the wire."""

    def __init__(self, engine: Engine):
        self.engine = engine
        # Auto-create tables on init. Idempotent — safe to call repeatedly.
        # For Postgres production with Alembic, this becomes a no-op since
        # the tables already exist from the migration.
        Base.metadata.create_all(engine)

    # ---- Node logbook ------------------------------------------------

    def upsert_node(self, signal: Signal) -> None:
        """Insert or refresh a node row from a signal. Same pinch_id →
        update last_seen and any newly-known name/layer."""
        try:
            with Session(self.engine) as session:
                existing = session.get(PlexusNode, signal.pinch_id)
                if existing:
                    existing.last_seen = _now()
                    if signal.name and not existing.name:
                        existing.name = signal.name
                    if signal.layer and not existing.layer:
                        existing.layer = signal.layer
                else:
                    session.add(
                        PlexusNode(
                            pinch_id=signal.pinch_id,
                            name=signal.name,
                            layer=signal.layer,
                            source_file=signal.source_file,
                            source_function=signal.source_function,
                            source_line=signal.source_line,
                        )
                    )
                session.commit()
        except Exception as e:
            log.warning(f"upsert_node failed for {signal.pinch_id}: {e}")

    def get_all_nodes(self) -> list[PlexusNode]:
        with Session(self.engine) as session:
            return list(session.execute(select(PlexusNode)).scalars().all())

    def get_node(self, pinch_id: str) -> Optional[PlexusNode]:
        with Session(self.engine) as session:
            return session.get(PlexusNode, pinch_id)

    # ---- Action audit log --------------------------------------------

    def log_action(
        self,
        signal: Signal,
        action_name: str,
        batch_name: Optional[str],
        ok: bool,
        detail: Optional[str] = None,
    ) -> None:
        """One row per action execution. Carries the full signal context
        so downstream queries don't need joins."""
        try:
            with Session(self.engine) as session:
                session.add(
                    PlexusActionLog(
                        pinch_id=signal.pinch_id,
                        signal_id=uuid.UUID(signal.signal_id),
                        action_name=action_name,
                        batch_name=batch_name,
                        payload=signal.payload,
                        severity=signal.severity.value,
                        layer=signal.layer,
                        node_name=signal.name,
                        source_file=signal.source_file,
                        source_function=signal.source_function,
                        source_line=signal.source_line,
                        ok=ok,
                        detail=detail,
                    )
                )
                session.commit()
        except Exception as e:
            log.warning(f"log_action failed for {action_name}: {e}")

    def get_action_log(
        self,
        action_name: Optional[str] = None,
        pinch_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[PlexusActionLog]:
        with Session(self.engine) as session:
            q = (
                select(PlexusActionLog)
                .order_by(PlexusActionLog.executed_at.desc())
                .limit(limit)
            )
            if action_name:
                q = q.where(PlexusActionLog.action_name == action_name)
            if pinch_id:
                q = q.where(PlexusActionLog.pinch_id == pinch_id)
            return list(session.execute(q).scalars().all())

    # ---- Topology views ----------------------------------------------

    def save_topology_view(
        self,
        name: str,
        layout_json: dict,
        description: Optional[str] = None,
    ) -> str:
        with Session(self.engine) as session:
            view = PlexusTopologyView(
                name=name,
                description=description,
                layout_json=layout_json,
            )
            session.add(view)
            session.commit()
            return str(view.id)

    def get_topology_views(self) -> list[PlexusTopologyView]:
        with Session(self.engine) as session:
            return list(
                session.execute(
                    select(PlexusTopologyView).order_by(
                        PlexusTopologyView.updated_at.desc()
                    )
                )
                .scalars()
                .all()
            )

    def get_topology_view(self, view_id: str) -> Optional[PlexusTopologyView]:
        with Session(self.engine) as session:
            return session.get(PlexusTopologyView, uuid.UUID(view_id))

    def update_topology_view(self, view_id: str, layout_json: dict) -> None:
        with Session(self.engine) as session:
            view = session.get(PlexusTopologyView, uuid.UUID(view_id))
            if view:
                view.layout_json = layout_json
                view.updated_at = _now()
                session.commit()

    def delete_topology_view(self, view_id: str) -> None:
        with Session(self.engine) as session:
            view = session.get(PlexusTopologyView, uuid.UUID(view_id))
            if view:
                session.delete(view)
                session.commit()
