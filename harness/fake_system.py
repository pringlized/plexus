import random
from plexus.models import Severity


class FakeSecurityScanner:
    NODE_ID = "sec-gate-01"

    MESSAGES = [
        # 15 clean
        (Severity.INFO, "scan.clean", {"doc_id": "doc-881", "scan_ms": 0.2}),
        (Severity.INFO, "scan.clean", {"doc_id": "doc-882", "scan_ms": 0.3}),
        (Severity.INFO, "scan.clean", {"doc_id": "doc-883", "scan_ms": 0.4}),
        (Severity.INFO, "scan.clean", {"doc_id": "doc-884", "scan_ms": 0.2}),
        (Severity.INFO, "scan.clean", {"doc_id": "doc-885", "scan_ms": 0.3}),
        (Severity.INFO, "scan.clean", {"doc_id": "doc-886", "scan_ms": 0.2}),
        (Severity.INFO, "scan.clean", {"doc_id": "doc-887", "scan_ms": 0.5}),
        (Severity.INFO, "scan.clean", {"doc_id": "doc-888", "scan_ms": 0.3}),
        (Severity.INFO, "scan.clean", {"doc_id": "doc-889", "scan_ms": 0.2}),
        (Severity.INFO, "scan.clean", {"doc_id": "doc-890", "scan_ms": 0.4}),
        (Severity.INFO, "scan.clean", {"doc_id": "doc-891", "scan_ms": 0.3}),
        (Severity.INFO, "scan.clean", {"doc_id": "doc-892", "scan_ms": 0.2}),
        (Severity.NOTICE, "scan.strip", {"doc_id": "doc-893", "chars_stripped": 2, "scan_ms": 0.4}),
        (Severity.NOTICE, "scan.strip", {"doc_id": "doc-894", "chars_stripped": 1, "scan_ms": 0.3}),
        (Severity.NOTICE, "scan.strip", {"doc_id": "doc-895", "chars_stripped": 3, "scan_ms": 0.5}),
        # 5 flaggable
        (Severity.CRITICAL, "scan.critical", {"doc_id": "doc-896", "threat": "invisible_unicode", "char": "U+FE01", "scan_ms": 0.4}),
        (Severity.CRITICAL, "scan.critical", {"doc_id": "doc-897", "threat": "glassworm_encoding", "char": "U+E0041", "scan_ms": 0.3}),
        (Severity.WARNING,  "scan.homoglyph", {"doc_id": "doc-898", "threat": "homoglyph", "char": "U+0430", "word": "anthropic", "scan_ms": 0.5}),
        (Severity.ANOMALY,  "scan.bidi", {"doc_id": "doc-899", "threat": "bidi_override", "char": "U+202E", "scan_ms": 0.4}),
        (Severity.WARNING,  "scan.homoglyph", {"doc_id": "doc-900", "threat": "homoglyph", "char": "U+043E", "word": "google", "scan_ms": 0.3}),
    ]

    def random_message(self):
        return random.choice(self.MESSAGES)


class FakeIngestionPipeline:
    NODE_ID = "ing-pipeline-01"

    MESSAGES = [
        # 15 clean
        (Severity.INFO, "document.received",  {"doc_id": "doc-101", "source": "upload", "size_kb": 42}),
        (Severity.INFO, "document.received",  {"doc_id": "doc-102", "source": "upload", "size_kb": 18}),
        (Severity.INFO, "document.received",  {"doc_id": "doc-103", "source": "api",    "size_kb": 95}),
        (Severity.INFO, "document.received",  {"doc_id": "doc-104", "source": "upload", "size_kb": 31}),
        (Severity.INFO, "document.received",  {"doc_id": "doc-105", "source": "upload", "size_kb": 67}),
        (Severity.INFO, "document.processed", {"doc_id": "doc-101", "chunks": 12, "ms": 210}),
        (Severity.INFO, "document.processed", {"doc_id": "doc-102", "chunks": 5,  "ms": 98}),
        (Severity.INFO, "document.processed", {"doc_id": "doc-103", "chunks": 28, "ms": 445}),
        (Severity.INFO, "document.processed", {"doc_id": "doc-104", "chunks": 9,  "ms": 167}),
        (Severity.INFO, "document.processed", {"doc_id": "doc-105", "chunks": 19, "ms": 312}),
        (Severity.NOTICE, "document.slow",    {"doc_id": "doc-106", "ms": 1200, "threshold_ms": 1000}),
        (Severity.NOTICE, "document.slow",    {"doc_id": "doc-107", "ms": 1450, "threshold_ms": 1000}),
        (Severity.INFO, "document.received",  {"doc_id": "doc-108", "source": "api", "size_kb": 204}),
        (Severity.INFO, "document.received",  {"doc_id": "doc-109", "source": "upload", "size_kb": 55}),
        (Severity.INFO, "document.processed", {"doc_id": "doc-108", "chunks": 61, "ms": 890}),
        # 5 flaggable
        (Severity.CRITICAL, "document.failed",   {"doc_id": "doc-110", "error": "parse_error", "detail": "malformed UTF-8"}),
        (Severity.ANOMALY,  "pipeline.stalled",  {"stage": "chunking", "stuck_for_s": 45, "doc_id": "doc-111"}),
        (Severity.ANOMALY,  "pipeline.stalled",  {"stage": "embedding", "stuck_for_s": 62, "doc_id": "doc-112"}),
        (Severity.CRITICAL, "document.rejected", {"doc_id": "doc-113", "reason": "schema_violation", "field": "content"}),
        (Severity.WARNING,  "document.oversized", {"doc_id": "doc-114", "size_kb": 8200, "limit_kb": 5000}),
    ]

    def random_message(self):
        return random.choice(self.MESSAGES)


class FakeBuildEngine:
    NODE_ID = "build-engine-01"

    MESSAGES = [
        # 15 clean
        (Severity.INFO,   "dependency.resolved",  {"dep": "sqlalchemy", "version": "2.0.1"}),
        (Severity.INFO,   "dependency.resolved",  {"dep": "pydantic",   "version": "2.5.0"}),
        (Severity.INFO,   "dependency.resolved",  {"dep": "fastapi",    "version": "0.110.0"}),
        (Severity.INFO,   "stage.started",        {"stage": "compile",  "target": "plexus-core"}),
        (Severity.INFO,   "stage.completed",      {"stage": "compile",  "target": "plexus-core", "ms": 1240}),
        (Severity.INFO,   "stage.started",        {"stage": "test",     "target": "plexus-core"}),
        (Severity.INFO,   "stage.completed",      {"stage": "test",     "target": "plexus-core", "ms": 3200, "passed": 42}),
        (Severity.INFO,   "artifact.created",     {"artifact": "plexus-0.1.0.tar.gz", "size_kb": 48}),
        (Severity.NOTICE, "stage.slow",           {"stage": "test", "ms": 8200, "threshold_ms": 5000}),
        (Severity.INFO,   "dependency.resolved",  {"dep": "uvicorn",    "version": "0.29.0"}),
        (Severity.INFO,   "stage.started",        {"stage": "lint",     "target": "plexus-core"}),
        (Severity.INFO,   "stage.completed",      {"stage": "lint",     "target": "plexus-core", "ms": 410}),
        (Severity.INFO,   "dependency.resolved",  {"dep": "httpx",      "version": "0.27.0"}),
        (Severity.INFO,   "stage.started",        {"stage": "package",  "target": "plexus-core"}),
        (Severity.INFO,   "stage.completed",      {"stage": "package",  "target": "plexus-core", "ms": 620}),
        # 5 flaggable
        (Severity.CRITICAL, "dependency.conflict", {"dep_a": "pydantic==1.10", "dep_b": "pydantic==2.5", "resolution": "failed"}),
        (Severity.ANOMALY,  "stage.failed",        {"stage": "test", "target": "plexus-core", "exit_code": 1, "failed_tests": 3}),
        (Severity.ANOMALY,  "stage.failed",        {"stage": "compile", "target": "plexus-node", "exit_code": 2, "error": "type_error"}),
        (Severity.WARNING,  "artifact.missing",    {"expected": "plexus-0.1.0.tar.gz", "stage": "package"}),
        (Severity.CRITICAL, "dependency.missing",  {"dep": "libsodium", "required_by": "plexus-crypto"}),
    ]

    def random_message(self):
        return random.choice(self.MESSAGES)


class FakeAgentWorker:
    NODE_ID = "agent-worker-01"

    MESSAGES = [
        # 15 clean
        (Severity.INFO,   "task.pickup",      {"task_id": "t-001", "type": "recon",   "agent": "cc"}),
        (Severity.INFO,   "task.completed",   {"task_id": "t-001", "duration_s": 4.2, "agent": "cc"}),
        (Severity.INFO,   "task.pickup",      {"task_id": "t-002", "type": "build",   "agent": "cc"}),
        (Severity.INFO,   "tool.called",      {"task_id": "t-002", "tool": "Read",    "path": "src/main.rs"}),
        (Severity.INFO,   "tool.called",      {"task_id": "t-002", "tool": "Grep",    "pattern": "fn handle"}),
        (Severity.INFO,   "task.completed",   {"task_id": "t-002", "duration_s": 12.7, "agent": "cc"}),
        (Severity.INFO,   "task.pickup",      {"task_id": "t-003", "type": "eval",    "agent": "cc"}),
        (Severity.INFO,   "tool.called",      {"task_id": "t-003", "tool": "Read",    "path": "specs/plexus.md"}),
        (Severity.INFO,   "task.completed",   {"task_id": "t-003", "duration_s": 6.1, "agent": "cc"}),
        (Severity.NOTICE, "context.high",     {"task_id": "t-004", "utilization_pct": 78, "agent": "cc"}),
        (Severity.INFO,   "task.pickup",      {"task_id": "t-005", "type": "recon",   "agent": "cc"}),
        (Severity.INFO,   "tool.called",      {"task_id": "t-005", "tool": "Glob",    "pattern": "**/*.rs"}),
        (Severity.INFO,   "task.completed",   {"task_id": "t-005", "duration_s": 2.9, "agent": "cc"}),
        (Severity.INFO,   "task.pickup",      {"task_id": "t-006", "type": "build",   "agent": "cc"}),
        (Severity.INFO,   "task.completed",   {"task_id": "t-006", "duration_s": 8.4, "agent": "cc"}),
        # 5 flaggable
        (Severity.CRITICAL, "task.failed",    {"task_id": "t-007", "error": "context_exceeded", "agent": "cc"}),
        (Severity.ANOMALY,  "agent.idle",     {"agent": "cc", "idle_s": 120, "threshold_s": 60}),
        (Severity.ANOMALY,  "tool.error",     {"task_id": "t-008", "tool": "Read", "error": "file_not_found", "path": "src/missing.rs"}),
        (Severity.WARNING,  "context.high",   {"task_id": "t-009", "utilization_pct": 94, "agent": "cc"}),
        (Severity.CRITICAL, "agent.crash",    {"agent": "cc", "task_id": "t-010", "signal": "SIGSEGV"}),
    ]

    def random_message(self):
        return random.choice(self.MESSAGES)


class FakeHealthMonitor:
    NODE_ID = "health-monitor-01"

    MESSAGES = [
        # 15 clean
        (Severity.INFO, "heartbeat",         {"service": "plexus-hub",   "uptime_s": 3600}),
        (Severity.INFO, "heartbeat",         {"service": "plexus-hub",   "uptime_s": 3660}),
        (Severity.INFO, "heartbeat",         {"service": "plexus-hub",   "uptime_s": 3720}),
        (Severity.INFO, "resource.ok",       {"service": "plexus-hub",   "cpu_pct": 12, "mem_mb": 84}),
        (Severity.INFO, "resource.ok",       {"service": "plexus-hub",   "cpu_pct": 14, "mem_mb": 86}),
        (Severity.INFO, "heartbeat",         {"service": "fake-system",  "uptime_s": 1200}),
        (Severity.INFO, "heartbeat",         {"service": "fake-system",  "uptime_s": 1260}),
        (Severity.INFO, "resource.ok",       {"service": "fake-system",  "cpu_pct": 8,  "mem_mb": 120}),
        (Severity.INFO, "connectivity.ok",   {"host": "localhost",       "latency_ms": 1}),
        (Severity.INFO, "connectivity.ok",   {"host": "localhost",       "latency_ms": 2}),
        (Severity.INFO, "heartbeat",         {"service": "plexus-hub",   "uptime_s": 3780}),
        (Severity.INFO, "resource.ok",       {"service": "plexus-hub",   "cpu_pct": 11, "mem_mb": 85}),
        (Severity.INFO, "heartbeat",         {"service": "fake-system",  "uptime_s": 1320}),
        (Severity.INFO, "resource.ok",       {"service": "fake-system",  "cpu_pct": 9,  "mem_mb": 122}),
        (Severity.INFO, "connectivity.ok",   {"host": "localhost",       "latency_ms": 1}),
        # 5 flaggable
        (Severity.CRITICAL, "service.down",  {"service": "plexus-hub",  "last_seen_s": 45}),
        (Severity.ANOMALY,  "resource.high", {"service": "fake-system", "cpu_pct": 94, "mem_mb": 980, "threshold_cpu": 90}),
        (Severity.ANOMALY,  "resource.high", {"service": "plexus-hub",  "cpu_pct": 91, "mem_mb": 512, "threshold_cpu": 90}),
        (Severity.WARNING,  "heartbeat.late",{"service": "fake-system", "expected_s": 30, "actual_s": 55}),
        (Severity.CRITICAL, "disk.full",     {"mount": "/", "used_pct": 97, "free_mb": 210}),
    ]

    def random_message(self):
        return random.choice(self.MESSAGES)
