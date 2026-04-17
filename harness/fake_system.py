"""Ten distinct pinch call sites — each function is its own call site so
every one produces a unique, stable pinch_id hash. A random gateway picks
one per tick."""

import random

from plexus import PlexusHub, Severity

DOC_IDS = [f"doc-{n}" for n in range(800, 900)]
TASK_IDS = [f"t-{n:03d}" for n in range(1, 60)]


def _doc() -> str:
    return random.choice(DOC_IDS)


def _task() -> str:
    return random.choice(TASK_IDS)


# ---------- Security ----------------------------------------------------


def scan_clean(hub: PlexusHub) -> None:
    hub.pinch(
        payload={"doc_id": _doc(), "scan_ms": round(random.uniform(0.1, 0.5), 2)},
        severity=Severity.INFO,
        layer="security",
        name="Security scan clean",
    )


def scan_critical(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "doc_id": _doc(),
            "threat": "invisible_unicode",
            "char": "U+FE01",
            "scan_ms": round(random.uniform(0.3, 0.6), 2),
        },
        severity=Severity.CRITICAL,
        layer="security",
        action="security-critical-response",
        name="Security scan critical",
    )


def auth_session_ok(hub: PlexusHub) -> None:
    hub.pinch(
        payload={"user_id": f"u-{random.randint(1000, 9999)}"},
        severity=Severity.INFO,
        layer="security",
        name="Auth session accepted",
    )


# ---------- Ingestion ---------------------------------------------------


def ingest_received(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "doc_id": _doc(),
            "source": random.choice(["upload", "api"]),
            "size_kb": random.randint(5, 250),
        },
        severity=Severity.INFO,
        layer="ingestion",
        name="Ingestion document received",
    )


def ingest_stalled(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "stage": random.choice(["chunking", "embedding"]),
            "stuck_for_s": random.randint(30, 90),
            "doc_id": _doc(),
        },
        severity=Severity.ANOMALY,
        layer="ingestion",
        name="Ingestion pipeline stalled",
    )


# ---------- Build -------------------------------------------------------


def build_dep_resolved(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "dep": random.choice(["pydantic", "httpx", "svelte", "vite", "fastapi"]),
            "version": f"{random.randint(1, 5)}.{random.randint(0, 20)}.{random.randint(0, 9)}",
        },
        severity=Severity.INFO,
        layer="build",
        name="Build dependency resolved",
    )


def build_failed(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "stage": random.choice(["compile", "test", "package"]),
            "exit_code": random.choice([1, 2, 127]),
            "error": random.choice(["type_error", "assertion_failed", "missing_dep"]),
        },
        severity=Severity.CRITICAL,
        layer="build",
        name="Build stage failed",
    )


# ---------- Agent -------------------------------------------------------


def agent_task_pickup(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "task_id": _task(),
            "type": random.choice(["recon", "build", "eval"]),
            "agent": "cc",
        },
        severity=Severity.INFO,
        layer="agent",
        name="Agent task pickup",
    )


# ---------- Health ------------------------------------------------------


def health_heartbeat(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "service": random.choice(["plexus-hub", "fake-system", "ui-demo"]),
            "uptime_s": random.randint(60, 86400),
        },
        severity=Severity.INFO,
        layer="health",
        name="Health heartbeat",
    )


def health_service_down(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "service": random.choice(["plexus-hub", "fake-system"]),
            "last_seen_s": random.randint(30, 120),
        },
        severity=Severity.CRITICAL,
        layer="health",
        name="Health service down",
    )


# ---------- Randomization gateway ---------------------------------------

# Weighted list so pings dominate (mirrors reality) and flaggable signals
# still surface often enough to see the action/batch paths fire.
_WEIGHTED: list[tuple[float, callable]] = [
    (10.0, scan_clean),
    (1.2, scan_critical),
    (4.0, auth_session_ok),
    (6.0, ingest_received),
    (1.0, ingest_stalled),
    (5.0, build_dep_resolved),
    (0.8, build_failed),
    (4.0, agent_task_pickup),
    (6.0, health_heartbeat),
    (0.6, health_service_down),
]


def fire_random(hub: PlexusHub) -> None:
    total = sum(w for w, _ in _WEIGHTED)
    pick = random.uniform(0, total)
    running = 0.0
    for weight, fn in _WEIGHTED:
        running += weight
        if pick <= running:
            fn(hub)
            return
    # Fallback (should never hit due to floating arithmetic).
    _WEIGHTED[-1][1](hub)
