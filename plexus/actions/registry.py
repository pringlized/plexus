from pydantic import BaseModel, ConfigDict, field_validator

from plexus.actions.base import BaseAction
from plexus.actions.invoke_build_fixer import InvokeBuildFixerAction
from plexus.actions.notify_ops import NotifyOpsAction
from plexus.actions.quarantine_document import QuarantineDocumentAction
from plexus.actions.reboot_redis import RebootRedisServerAction
from plexus.actions.scale_embed_workers import ScaleEmbedWorkersAction
from plexus.actions.security_agent import SecurityAgentAction


class ActionRegistry(BaseModel):
    """Maps an action name (as declared in YAML) directly to its adapter class.

    No type indirection. The name IS the adapter. If you want two
    TelegramAction wirings to different channels, write two adapter
    classes (or teach one adapter to read per-instance config itself).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    classes: dict[str, type[BaseAction]]

    @field_validator("classes")
    @classmethod
    def _must_be_action_subclass(
        cls, v: dict[str, type[BaseAction]]
    ) -> dict[str, type[BaseAction]]:
        for name, action_cls in v.items():
            if not isinstance(action_cls, type) or not issubclass(action_cls, BaseAction):
                raise ValueError(
                    f"'{name}' must map to a BaseAction subclass, got {action_cls!r}"
                )
        return v

    def get(self, name: str) -> type[BaseAction]:
        cls = self.classes.get(name)
        if not cls:
            raise ValueError(
                f"Unknown action: '{name}'. Register it in plexus/actions/registry.py"
            )
        return cls

    def register(self, name: str, action_cls: type[BaseAction]) -> None:
        self.classes = {**self.classes, name: action_cls}


ACTION_REGISTRY = ActionRegistry(
    classes={
        "dispatch-security-agent": SecurityAgentAction,
        "reboot-redis-server": RebootRedisServerAction,
        "notify-ops": NotifyOpsAction,
        "invoke-build-fixer": InvokeBuildFixerAction,
        "quarantine-document": QuarantineDocumentAction,
        "scale-embed-workers": ScaleEmbedWorkersAction,
    }
)


def get_action_class(name: str) -> type[BaseAction]:
    return ACTION_REGISTRY.get(name)
