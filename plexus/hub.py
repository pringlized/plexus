import hashlib
import inspect
import logging

from pydantic import BaseModel

from plexus import config
from plexus.actions.base import BaseAction
from plexus.actions.registry import get_action_class
from plexus.loader import load_config
from plexus.logging_config import configure_logging
from plexus.models import (
    ActionResult,
    Severity,
    Signal,
    WireActionResult,
    WireEvent,
)

logger = logging.getLogger(config.LOGGER_NAME)


def _compute_pinch_id(source_file: str, source_function: str, source_line: int) -> str:
    """Stable sha256[:12] of file:function:line — same line always same id."""
    raw = f"{source_file}:{source_function}:{source_line}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:12]


class PlexusHub:
    def __init__(
        self,
        action_config: str | None = None,
        ui_endpoint: str | None = None,
    ):
        # Library owns its own log file. Wires a file handler on the
        # plexus.* logger the first time a hub is instantiated.
        configure_logging()

        # Precedence: explicit arg > env var > default ("plexus-actions.yaml")
        self.config = load_config(action_config or config.ACTION_CONFIG)
        # Precedence: explicit arg > env var > None (no POST)
        self.ui_endpoint = ui_endpoint or config.UI_ENDPOINT
        self._sequences: dict[str, int] = {}
        self._action_instances = self._init_actions()

    def _init_actions(self) -> dict[str, BaseAction]:
        instances: dict[str, BaseAction] = {}
        for action_id, cfg in self.config.actions.items():
            if not cfg.enabled:
                logger.info(f"[action] '{action_id}' disabled — skipping init")
                continue
            cls = get_action_class(action_id)
            instances[action_id] = cls(action_id=action_id, hub=self)

        # Reject collisions — a single name can't be both an action and a batch.
        overlap = set(instances) & set(self.config.batches)
        if overlap:
            raise ValueError(
                f"action and batch share name(s): {sorted(overlap)}. "
                f"Rename one side in plexus-actions.yaml."
            )
        return instances

    # ---- Public surface ------------------------------------------------

    def pinch(
        self,
        payload: dict,
        severity: Severity,
        layer: str | None = None,
        action: str | None = None,
        name: str | None = None,
    ) -> None:
        # Capture call site — file:line:function where pinch() was called
        frame = inspect.stack()[1]
        source_file = frame.filename
        source_line = frame.lineno
        source_function = frame.function

        pinch_id = _compute_pinch_id(source_file, source_function, source_line)

        seq = self._sequences.get(pinch_id, 0) + 1
        self._sequences[pinch_id] = seq

        signal = Signal(
            pinch_id=pinch_id,
            name=name,
            source_file=source_file,
            source_line=source_line,
            source_function=source_function,
            severity=severity,
            layer=layer,
            payload=payload,
            sequence=seq,
        )

        logger.info(
            f"[pinch] {pinch_id}"
            + (f" name={name!r}" if name else "")
            + f" severity={severity.value} layer={layer or '-'} "
            f"src={_basename(source_file)}:{source_line} fn={source_function}"
        )

        action_results: list[ActionResult] = []
        resolved_batch: str | None = None

        if action:
            # action param accepts either a single action name or a batch name.
            if action in self._action_instances:
                action_results.append(self._fire_action(action, signal))
            elif action in self.config.batches:
                resolved_batch = action
                action_results.extend(self._fire_batch(action, signal))
            else:
                logger.warning(
                    f"[hub] unknown action or batch '{action}' "
                    f"(signal={signal.signal_id}) — skipping"
                )

        # Build the rolled-up wire result. Strict: any failure = batch failed.
        wire_action_result: WireActionResult | None = None
        if action and action_results:
            failed_details = [
                r.detail for r in action_results if not r.ok and r.detail
            ]
            wire_action_result = WireActionResult(
                batch=resolved_batch,
                actions_fired=[r.action_id for r in action_results],
                ok=all(r.ok for r in action_results),
                detail="; ".join(failed_details) or None,
            )

        event = WireEvent(
            pinch_id=signal.pinch_id,
            name=signal.name,
            layer=signal.layer,
            severity=signal.severity,
            source_file=signal.source_file,
            source_line=signal.source_line,
            source_function=signal.source_function,
            payload=signal.payload,
            timestamp=signal.timestamp,
            action=action,
            action_result=wire_action_result,
        )
        self._post_to_ui(event)

    # ---- Dispatch ------------------------------------------------------

    def _fire_action(self, action_id: str, signal: Signal) -> ActionResult:
        instance = self._action_instances.get(action_id)
        if not instance:
            logger.warning(
                f"[hub] unknown or disabled action '{action_id}' — skipping "
                f"(signal={signal.signal_id})"
            )
            return ActionResult(
                action_id=action_id,
                signal_id=signal.signal_id,
                ok=False,
                detail="unknown or disabled action",
            )

        logger.info(f"[action] firing '{action_id}' for signal {signal.signal_id}")
        try:
            result = instance.execute(signal)
        except Exception as e:  # one bad action must not nuke the batch
            logger.exception(f"[action] '{action_id}' raised: {e}")
            return ActionResult(
                action_id=action_id,
                signal_id=signal.signal_id,
                ok=False,
                detail=f"exception: {e}",
            )

        logger.info(
            f"[action] '{action_id}' → ok={result.ok}"
            + (f" detail={result.detail}" if result.detail else "")
        )
        return result

    def _fire_batch(self, batch_id: str, signal: Signal) -> list[ActionResult]:
        batch_cfg = self.config.batches.get(batch_id)
        if not batch_cfg:
            logger.warning(f"[hub] unknown batch '{batch_id}' — skipping")
            return [
                ActionResult(
                    action_id=batch_id,
                    signal_id=signal.signal_id,
                    ok=False,
                    detail=f"unknown batch '{batch_id}'",
                )
            ]

        logger.info(
            f"[batch] executing '{batch_id}' ({len(batch_cfg.actions)} actions) "
            f"for signal {signal.signal_id}"
        )
        return [self._fire_action(aid, signal) for aid in batch_cfg.actions]

    # ---- Wire ----------------------------------------------------------

    def _post_to_ui(self, event: BaseModel) -> None:
        """Fire-and-forget POST to the UI. Never raises."""
        if not self.ui_endpoint:
            return
        try:
            import httpx

            httpx.post(
                self.ui_endpoint,
                json=event.model_dump(mode="json"),
                timeout=config.HTTPX_TIMEOUT,
            )
        except Exception:
            # UI being down never affects the hub.
            pass


def _basename(path: str) -> str:
    return path.rsplit("/", 1)[-1]
