"""Centralized environment-driven configuration.

Everything Plexus reads from env lives here. Keeps os.environ calls out
of the rest of the library and makes the config surface discoverable.

Reads a local .env file if present (handled by python-dotenv).
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

# Read .env once at import time. No-op if the file doesn't exist.
load_dotenv()


# Where the hub POSTs live signal events. Unset → hub emits nothing
# over HTTP; receptors still route normally.
UI_ENDPOINT: str | None = os.environ.get("PLEXUS_UI_ENDPOINT")

# Logger namespace for the hub and built-in receptors.
LOGGER_NAME: str = os.environ.get("PLEXUS_LOGGER_NAME", "plexus")

# httpx.post timeout in seconds for the fire-and-forget UI POST.
# Short on purpose — keeps pinch() fast when the UI is unreachable.
HTTPX_TIMEOUT: float = float(os.environ.get("PLEXUS_HTTPX_TIMEOUT", "0.5"))

# Central log file written by the hub. Every pinch, batch, and action
# logged under the plexus.* namespace lands here. Set empty string to
# disable the library's file handler entirely.
LOG_FILE: str = os.environ.get("PLEXUS_LOG_FILE", "logs/plexus.log")

# Log level for the plexus.* namespace.
LOG_LEVEL: str = os.environ.get("PLEXUS_LOG_LEVEL", "INFO").upper()

# Path to the YAML file that declares actions and batches.
ACTION_CONFIG: str = os.environ.get("PLEXUS_ACTION_CONFIG", "plexus-actions.yaml")
