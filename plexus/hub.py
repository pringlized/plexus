from plexus.models import Signal, Severity
from plexus.loader import load_config
from plexus.adapters import get_receptor_class
import logging

logger = logging.getLogger("plexus")


class PlexusHub:
    def __init__(self, nodes_path: str, receptors_path: str):
        self.config = load_config(nodes_path, receptors_path)
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
        )

        receptor_ids = self._routing_table.get(node_short_id, [])

        if not receptor_ids:
            # no receptors wired — /dev/null
            return

        for rid in receptor_ids:
            receptor = self._receptor_instances[rid]
            result = receptor.receive(signal)
            logger.info(
                f"[{signal.node_short_id}] → [{rid}] "
                f"severity={signal.severity.value} "
                f"category={signal.category} "
                f"action={result.action}"
                + (f" reason={result.flag_reason}" if result.flag_reason else "")
            )
            # WEBSOCKET COMING SOON
