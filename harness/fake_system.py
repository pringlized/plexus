"""Meridian — fictional AI platform fake system harness.
Thirteen distinct pinch call sites across five layers.
Each function is its own call site — unique stable pinch_id per function.
A weighted gateway fires one per tick."""

import random

from plexus import PlexusHub, Severity

DOC_IDS  = [f"doc-{n}" for n in range(800, 950)]
TASK_IDS = [f"t-{n:03d}" for n in range(1, 80)]
BUILD_IDS = [f"build-{n:04d}" for n in range(1000, 1100)]


def _doc()   -> str: return random.choice(DOC_IDS)
def _task()  -> str: return random.choice(TASK_IDS)
def _build() -> str: return random.choice(BUILD_IDS)


# ── Security ─────────────────────────────────────────────────────────────────

def scan_clean(hub: PlexusHub) -> None:
    hub.pinch(
        payload={"doc_id": _doc(), "scan_ms": round(random.uniform(0.1, 0.5), 2)},
        severity=Severity.INFO,
        layer="security",
        name="Security gate — clean scan",
    )


def scan_critical(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "doc_id": _doc(),
            "threat": random.choice(["invisible_unicode", "glassworm_encoding", "bidi_override"]),
            "char": random.choice(["U+FE01", "U+E0041", "U+202E", "U+0430"]),
            "scan_ms": round(random.uniform(0.3, 0.6), 2),
        },
        severity=Severity.CRITICAL,
        layer="security",
        action="security-response",
        name="Security gate — critical threat",
    )


def auth_anomaly(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "user_id": f"u-{random.randint(1000, 9999)}",
            "ip": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "reason": random.choice([
                "unusual_hour", "multiple_failed_attempts",
                "new_device", "geo_anomaly"
            ]),
            "risk_score": round(random.uniform(0.7, 1.0), 2),
        },
        severity=Severity.ANOMALY,
        layer="security",
        action="security-response",
        name="Auth anomaly detected",
    )


# ── Ingestion ─────────────────────────────────────────────────────────────────

def ingest_received(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "doc_id": _doc(),
            "source": random.choice(["upload", "api", "email", "webhook"]),
            "size_kb": random.randint(5, 2048),
            "mime": random.choice(["application/pdf", "text/plain", "text/html"]),
        },
        severity=Severity.INFO,
        layer="ingestion",
        name="Document received",
    )


def embed_stalled(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "stage": "embedding",
            "stuck_for_s": random.randint(45, 180),
            "doc_id": _doc(),
            "queue_depth": random.randint(50, 500),
            "worker_count": random.randint(1, 4),
        },
        severity=Severity.ANOMALY,
        layer="ingestion",
        action="ingestion-alert",
        name="Embedding pipeline stalled",
    )


def chunk_violation(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "doc_id": _doc(),
            "chunk_size_tokens": random.randint(8000, 32000),
            "limit_tokens": 8192,
            "strategy": random.choice(["recursive", "sentence", "fixed"]),
        },
        severity=Severity.WARNING,
        layer="ingestion",
        action="ingestion-alert",
        name="Chunk size violation",
    )


# ── Build ─────────────────────────────────────────────────────────────────────

def build_dep_resolved(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "dep": random.choice([
                "pydantic", "httpx", "sqlalchemy", "alembic",
                "svelte", "vite", "tailwindcss", "better-sqlite3"
            ]),
            "version": f"{random.randint(1,5)}.{random.randint(0,20)}.{random.randint(0,9)}",
            "build_id": _build(),
        },
        severity=Severity.INFO,
        layer="build",
        name="Dependency resolved",
    )


def build_stage_failed(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "build_id": _build(),
            "stage": random.choice(["compile", "test", "lint", "package"]),
            "exit_code": random.choice([1, 2, 127]),
            "error": random.choice([
                "type_error", "assertion_failed",
                "missing_dep", "timeout", "oom"
            ]),
            "duration_s": random.randint(5, 120),
        },
        severity=Severity.CRITICAL,
        layer="build",
        action="build-failure-response",
        name="Build stage failed",
    )


def artifact_failed(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "build_id": _build(),
            "artifact": random.choice([
                "plexus-0.4.0.tar.gz",
                "ui-demo.zip",
                "praetor-node.bin"
            ]),
            "error": random.choice([
                "checksum_mismatch", "upload_timeout",
                "storage_quota_exceeded", "signing_failed"
            ]),
        },
        severity=Severity.CRITICAL,
        layer="build",
        action="build-failure-response",
        name="Artifact generation failed",
    )


# ── Agent ─────────────────────────────────────────────────────────────────────

def agent_task_pickup(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "task_id": _task(),
            "type": random.choice(["recon", "build", "eval", "fix"]),
            "agent": random.choice(["cc", "vector", "fixer-agent"]),
            "feature_id": random.randint(700, 999),
        },
        severity=Severity.INFO,
        layer="agent",
        name="Agent task pickup",
    )


def agent_context_overflow(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "task_id": _task(),
            "agent": random.choice(["cc", "vector", "fixer-agent"]),
            "context_tokens": random.randint(190000, 210000),
            "limit_tokens": 200000,
            "truncated_pct": round(random.uniform(0.05, 0.25), 2),
        },
        severity=Severity.WARNING,
        layer="agent",
        action="notify-ops",
        name="Agent context overflow",
    )


# ── Infrastructure ────────────────────────────────────────────────────────────

def redis_down(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "host": random.choice(["redis-prod-01", "redis-prod-02", "redis-cache-01"]),
            "port": 6379,
            "last_response_ms": random.randint(5000, 30000),
            "tcp_state": random.choice(["ECONNREFUSED", "TIMEOUT", "RST"]),
            "consecutive_failures": random.randint(3, 20),
            "affected_services": random.randint(1, 8),
        },
        severity=Severity.CRITICAL,
        layer="infrastructure",
        action="infra-critical",
        name="Redis unreachable",
    )


def postgres_pool_exhausted(hub: PlexusHub) -> None:
    hub.pinch(
        payload={
            "host": random.choice(["pg-primary", "pg-replica-01"]),
            "port": 5432,
            "pool_size": 20,
            "active_connections": random.randint(20, 20),
            "waiting_requests": random.randint(10, 150),
            "oldest_query_ms": random.randint(5000, 60000),
            "database": random.choice(["praetor", "plexus", "velma"]),
        },
        severity=Severity.CRITICAL,
        layer="infrastructure",
        action="infra-critical",
        name="Postgres pool exhausted",
    )


# ── Weighted gateway ──────────────────────────────────────────────────────────

# Pings dominate (mirrors reality). Flaggable signals surface often enough
# to see action/batch paths fire regularly.
_WEIGHTED: list[tuple[float, callable]] = [
    (12.0, scan_clean),          # security — most common, always clean
    (1.5,  scan_critical),       # security — critical, fires batch
    (1.2,  auth_anomaly),        # security — anomaly, fires batch
    (8.0,  ingest_received),     # ingestion — high volume ping
    (0.8,  embed_stalled),       # ingestion — anomaly, fires batch
    (1.0,  chunk_violation),     # ingestion — warning, fires batch
    (7.0,  build_dep_resolved),  # build — high volume ping
    (0.7,  build_stage_failed),  # build — critical, fires batch
    (0.5,  artifact_failed),     # build — critical, fires batch
    (6.0,  agent_task_pickup),   # agent — high volume ping
    (0.9,  agent_context_overflow), # agent — warning, fires action
    (0.6,  redis_down),          # infra — critical, fires batch
    (0.5,  postgres_pool_exhausted), # infra — critical, fires batch
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
    _WEIGHTED[-1][1](hub)
