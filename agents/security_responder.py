"""Security responder callable — invoked by SecurityAgentAction with the
full signal envelope. Right now this is a stub that logs what it would
have done; real agent behavior goes in here."""
import logging

from plexus import config
from plexus.models import Signal

log = logging.getLogger(f"{config.LOGGER_NAME}.security_responder")


def handle(signal: Signal, hub) -> None:
    """Receive a flagged security signal and respond.

    Has the complete signal envelope including file/line/function of the
    original pinch, so a real agent can jump straight to the right place
    in the codebase without investigation.
    """
    payload = signal.payload
    log.info(
        f"security responder engaged · pinch_id={signal.pinch_id} "
        f"severity={signal.severity.value}"
    )
    log.info(
        f"  call site: {signal.source_file}:{signal.source_line} "
        f"in {signal.source_function}"
    )
    log.info(f"  payload: {payload}")
    log.info(
        f"  would quarantine doc_id={payload.get('doc_id')!r} "
        f"and notify on-call; rev2 wires the real dispatch"
    )
