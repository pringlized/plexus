"""Reboots a Redis server in response to a pinch."""
import logging

from plexus import config
from plexus.actions.base import BaseAction
from plexus.models import ActionResult, Signal

log = logging.getLogger(f"{config.LOGGER_NAME}.reboot_redis")


class RebootRedisServerAction(BaseAction):
    def execute(self, signal: Signal) -> ActionResult:
        log.info("Rebooting redis..")
        return self._ok(signal, "Rebooting redis..")
