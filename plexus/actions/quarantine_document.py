"""Quarantines a document flagged by the ingestion pipeline.

Stand-in adapter — logs only."""
import logging

from plexus import config
from plexus.actions.base import BaseAction
from plexus.models import ActionResult, Signal

log = logging.getLogger(f"{config.LOGGER_NAME}.quarantine_document")


class QuarantineDocumentAction(BaseAction):
    def execute(self, signal: Signal) -> ActionResult:
        doc_id = signal.payload.get("doc_id", "<unknown>")
        log.info(f"quarantining document {doc_id} from {signal.source_function}")
        return self._ok(signal, f"document {doc_id} quarantined")
