import inspect
import logging

from plexus.adapters import get_receptor_class
from plexus.loader import load_config
from plexus.models import Severity, Signal

logger = logging.getLogger("plexus")


class PlexusHub:
    def __init__(
        self,
        nodes_path: str,
        receptors_path: str,
        ui_endpoint: str | None = "http://localhost:5180/api/signal",
    ):
        self.config = load_config(nodes_path, receptors_path)
        self.ui_endpoint = ui_endpoint
        self._sequences: dict[str, int] = {}
        self._receptor_instances = self._init_receptors()
        self._routing_table = self._build_routing_table()

    def _init_receptors(self):
        instances = {}
        for rid, rcfg in self.config.receptors.items():
            cls = get_receptor_class(rcfg.type)
            instances[rid] = cls(receptor_id=rid, config=rcfg)
        return instances

    def _build_routing_table(self) -> dict[str, list[str]]:
        # maps node_short_id → list of receptor_ids
        table: dict[str, list[str]] = {}
        for rid, rcfg in self.config.receptors.items():
            for node_id in rcfg.listens_to:
                table.setdefault(node_id, []).append(rid)
        return table

    def pinch(
        self,
        node_short_id: str,
        payload: dict,
        severity: Severity = Severity.INFO,
        category: str = "general",
    ) -> None:
        # Capture call site — the file:line where pinch() was called
        frame = inspect.stack()[1]
        source_file = frame.filename
        source_line = frame.lineno
        source_function = frame.function

        node = self.config.nodes.get(node_short_id)
        if not node:
            logger.warning(
                f"Plexus: unknown node id '{node_short_id}' — pinch ignored"
            )
            return

        seq = self._sequences.get(node_short_id, 0) + 1
        self._sequences[node_short_id] = seq

        signal = Signal(
            node_short_id=node_short_id,
            node_uuid=node.uuid,
            node_type=node.type,
            node_layer=node.layer,
            node_description=node.description,
            severity=severity,
            category=category,
            payload=payload,
            sequence=seq,
            source_file=source_file,
            source_line=source_line,
            source_function=source_function,
        )

        receptor_ids = self._routing_table.get(node_short_id, [])

        results = []
        for rid in receptor_ids:
            receptor = self._receptor_instances[rid]
            result = receptor.receive(signal)
            results.append(result)
            logger.info(
                f"[{signal.node_short_id}] → [{rid}] "
                f"severity={signal.severity.value} "
                f"category={signal.category} "
                f"action={result.action}"
                + (f" reason={result.flag_reason}" if result.flag_reason else "")
            )

        # Even if no receptors matched, we still emit the event so the UI
        # can show the broadcast.
        event = {
            "signal": signal.model_dump(mode="json"),
            "receptor_results": [
                {
                    "receptor_id": r.receptor_id,
                    "receptor_type": r.receptor_type,
                    "action": r.action,
                    "flag_reason": r.flag_reason,
                }
                for r in results
            ],
        }

        self._post_to_ui(event)

    def _post_to_ui(self, event: dict) -> None:
        """Fire-and-forget POST to the UI. Never raises."""
        if not self.ui_endpoint:
            return
        try:
            import httpx

            httpx.post(
                self.ui_endpoint,
                json=event,
                timeout=0.5,  # short timeout — UI may not be running
            )
        except Exception:
            # UI being down never affects the hub.
            pass
