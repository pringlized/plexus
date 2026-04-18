<p align="center">
  <img src="assets/plexus_readme_header_animated_v2.svg" alt="Plexus — Signal Nervous System" />
</p>

> *Decentralize the sensing. Centralize the picture.*

Plexus is an open-source signal nervous system for complex software. Drop a
single function call anywhere in your codebase — a **pinch** — and that
moment becomes a named, typed, traceable signal that flows through a central
hub and optionally triggers a real-world action.

Plexus is the wire. The wire does not decide what travels through it.

---

## The Problem

Complex systems accumulate blind spots. Logs exist but nobody watches them in
real time. Events happen but the connections between them are invisible.
Problems compound silently until they surface as incidents.

The traditional answer is monitoring dashboards — pull data periodically,
display it, hope someone is looking when something goes wrong.

**Plexus inverts this.** Every pinch is a live tap on a meaningful moment in
your code. The signal fires immediately. Actions respond in real time. The
system does not wait to be checked.

---

## How It Works

### One function call. That's the entire integration cost.

```python
from plexus import PlexusHub, Severity

hub = PlexusHub()

hub.pinch(
    payload={"doc_id": "doc-881", "threat": "homoglyph", "char": "U+0430", "scan_ms": 0.4},
    severity=Severity.CRITICAL,
    layer="security",
    name="Security scan critical",
    action="security-critical-response",
)
```

That's it. The developer drops a pinch at a meaningful point in their code
and walks away. Plexus handles everything else:

- Captures the exact **file, line, and function** where the pinch fired
- Generates a stable hash ID from the call site — no registration required
- Broadcasts the signal to the live UI
- Fires the named action or batch if one is specified
- Fires and forgets

The pinch never blocks. The pinch never waits. The pinch never cares what
happens downstream.

---

## Core Concepts

### The Pinch

```python
hub.pinch(
    payload,       # required — dict, unlimited k/v, JSON-serializable
    severity,      # required — info | notice | warning | anomaly | critical
    layer=None,    # optional — string, UI grouping
    action=None,   # optional — action or batch name
    name=None,     # optional — human label shown in CENTCOM
)
```

**`payload`** — required. Unlimited key/value pairs. No schema. No fixed
fields. No migrations. Pass whatever is meaningful at that point in the code.

**`severity`** — required. No default. The developer must be intentional.

**`layer`** — optional. Groups this signal visually in the UI. Any string.
Layers emerge automatically from the signal stream — nothing pre-declared.

**`action`** — optional. The name of an action or batch to fire. Plexus
looks up the name — action first, batch second. No action means the signal
is a ping: flows through, updates the UI, disappears.

**`name`** — optional. Human label shown in CENTCOM instead of the hash.

### The Ping

A pinch with no action is a ping. It flows through the hub, the UI reflects
it, and it disappears. This is the most common case. Heartbeats, clean scan
results, status updates — all pings. Presence and data. Nothing more.

### Node Identity — The Call Site Hash

Every unique pinch location has a stable identity derived automatically from
the call site:

```python
raw = f"{source_file}:{source_function}:{source_line}"
pinch_id = sha256(raw).hexdigest()[:12]  # e.g. "d2aec78bf786"
```

Same file, same function, same line — same ID. Every time. No registration.
No YAML entry. No boot sequence. The code creates the node by running.

Nodes appear in CENTCOM automatically the first time their pinch fires.
Plexus starts with zero nodes. The system picture builds itself.

### The Signal Envelope

Every signal carries:

| Field | Source | Description |
|---|---|---|
| `pinch_id` | auto | 12-char hash of file+function+line |
| `name` | caller | optional human label |
| `layer` | caller | optional grouping string |
| `severity` | caller | info / notice / warning / anomaly / critical |
| `payload` | caller | unlimited k/v dict |
| `source_file` | auto | file where hub.pinch() was called |
| `source_line` | auto | line number |
| `source_function` | auto | function name at call site |
| `timestamp` | auto | UTC at time of pinch |
| `action` | caller | optional action or batch name |

### The Hub

`PlexusHub` is the center. It receives every pinch, builds the signal
envelope, broadcasts to the UI, and fires the action or batch if one is
defined. It has no opinions. It does not evaluate signals. It does not
decide what matters.

### Actions — The Real Adapters

An action is a Python class with one job. It receives the full signal
envelope and does its specific thing.

```python
class BaseAction:
    def __init__(self, config: dict): ...
    def execute(self, signal: Signal) -> None: ...
```

Every action gets the complete signal. What it ignores is its own business.
If a developer wires the wrong action to a signal — that is the developer's
problem. **Plexus does not babysit.**

Actions are defined in `plexus-actions.yaml`:

```yaml
actions:
  dispatch-security-agent:
    enabled: true

  reboot-redis-server:
    enabled: true

batches:
  security-critical-response:
    - dispatch-security-agent
```

**Adding a new action:** one adapter class, one registry entry, one YAML
line. Plexus core does not change.

### Batches — Fan-Out

A batch is a named collection of actions. The same complete signal is
dispatched to every action in the batch simultaneously. Same signal. Every
action. In parallel.

### System Layers

Layers are strings on the pinch. Nothing more. Type a new layer name and it
appears in the topology, the dashboard health cards, and the nav on the next
signal. No registration. No migration. No restart.

Plexus starts with zero layers. They emerge from the signal stream.

---

## Configuration

One file. That is the complete configuration surface.

**`plexus-actions.yaml`** — actions and batches. What the system can do.

No node config file. No receptor config file. Nodes register themselves from
the signal stream. Layers emerge from the pinch. The code is the
configuration.

---

## CENTCOM — The Visual Operations Layer

Plexus ships a SvelteKit UI that builds itself from the live signal stream
and `plexus-actions.yaml`. Nothing is hardcoded. Nothing is pre-declared.

**On load:** zero nodes, zero layers. Actions and batches load from YAML.

**As signals arrive:** nodes appear in the nav, layers materialize as health
cards, the topology canvas populates automatically — grouped by layer,
colored by severity.

### Dashboard

Layer health cards emerge from the signal stream. Stats update live. Signal
feed shows every pinch with name, call site, and expandable payload.

### Topology

Nodes auto-place by layer on the left. Actions and batches appear on the
right. Edges animate when a batch fires. Node health rings pulse with
severity color. Critical nodes glow. Healthy nodes dim.

### Monitor

Three columns live: node broadcasts → action receipts → action results.
Every signal row shows `filename.py:line` from the call site. Click any row
to expand the full payload.

### Node Detail

Per-node signal history, call site, expandable payload on every signal.
The route exists the moment the first signal from that location arrives.

### Action & Batch Detail

Per-action invocation history, success rate, which nodes triggered it, what
payload came through. Per-batch execution history with full fan-out detail.

<p align="center">
  <img src="assets/plexus-dashboard.png" alt="Plexus Dashboard" />
  <br/>
  <em>Dashboard — layers emerge from the signal stream. Nothing pre-declared.</em>
</p>

<p align="center">
  <img src="assets/plexus-topology.png" alt="Plexus Topology" />
  <br/>
  <em>Topology — nodes auto-register from the signal stream. Actions and batches from YAML.</em>
</p>

---

## Running It

```bash
# Clone the repo
git clone https://github.com/pringlized/plexus.git
cd plexus

# Install the Python library
pip install -e .

# Terminal 1 — start the UI
cd ui-demo
npm install
npm run dev

# Terminal 2 — run the harness
cd ..
python harness/runner.py
```

The harness fires pinches across multiple fake system components — security
scanner, ingestion pipeline, build engine, agent worker, health monitor.
Each component has unique call sites producing unique node IDs. The UI
receives signals live and the system picture builds itself in real time.

Watch the topology populate. Watch layers materialize. Watch critical nodes
glow. Watch the security agent dispatch and log its response.

---

## Use Cases

### Knowledge Base Ingestion Security

Wire a character-level scanner such as
[glassglyph-scanner](https://github.com/pringlized/glassglyph-scanner) as a
security pinch on your ingestion pipeline. Every document scanned fires a
signal. A critical finding triggers an action that dispatches a security agent
with the full payload — doc ID, threat type, character, scan duration. The
agent knows exactly what happened, exactly where in the code it happened,
and exactly what to do about it. No log archaeology. No investigation.

### Agentic Workflow Observability

In multi-agent systems, individual agents operate in isolation. Plexus gives
you a unified live picture across all of them. Each agent drops pinches on
task pickup, tool calls, completion, and anomalous behavior. The call site
on every signal tells you not just that an agent acted but exactly which
line of code triggered it.

### Infrastructure Response Automation

A pinch fires when Redis becomes unreachable. The action is
`reboot-redis-server`. The adapter runs the reboot script. The result flows
back through the hub. CENTCOM shows the signal, the action, and the result.
The whole incident lifecycle visible in one place.

### Build Pipeline Intelligence

Pinch on dependency resolution, stage transitions, artifact generation, and
failures. When a build stage fails, the signal carries exit code, stage name,
and error detail. An action dispatches an ops agent with everything it needs.

### Any System That Produces Events

If your component has a moment worth watching, drop a pinch. Name it. Layer
it. Wire an action if needed. Plexus is not domain-specific. It carries
whatever you tell it to carry.

---

## Tech Stack

**Python Library**
- Python 3.11+
- Pydantic v2 — all models and signal envelope validation
- PyYAML — config loading
- httpx — fire-and-forget POST to UI

**UI**
- SvelteKit + Svelte 5
- Svelte Flow — topology canvas
- Tailwind CSS
- Lucide icons

---

## Project Status

Plexus is in active development.

**Current — working**
- `PlexusHub` — signal routing, action dispatch, fire-and-forget
- `hub.pinch()` with automatic call site capture (file:line:function)
- Call site hash as stable node identity — no registration required
- Unlimited k/v payload
- Actions and batches — adapter pattern, fan-out
- SvelteKit CENTCOM UI — zero state on load, nodes auto-register from stream
- Live signal flow: pinch → hub → HTTP POST → SSE → browser store → UI
- Node, action, and batch detail pages with live data and expandable payloads

**Coming next**
- Logbook table — node hash registry with TTL, first seen, last seen
- Actions audit table — every action executed, signal that triggered it,
  result, timestamp
- Custom topology views — drag, group, name, save layouts
- Plexus drops into Praetor — first live production deployment

Contributions, feedback, and discussion welcome.

---

## Philosophy

Most observability platforms try to be smart. They correlate for you, decide
what critical means, ship opinions about what your system should look like.
You inherit their assumptions and anything that doesn't fit drops out of view.

Plexus stays deliberately simple. Three primitives: the pinch, the hub, the
action. The hub has no opinions. The code owns the node identity. The action
owns the response logic. The pinch owns nothing except the moment it marks.

One YAML file. An LLM can write it in two minutes. Git tracks every change.
The system picture is always honest because it has nowhere to hide.

The restraint is the point.

---

## License

MIT. See `LICENSE`.