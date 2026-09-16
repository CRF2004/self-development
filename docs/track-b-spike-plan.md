# Track B — Phase 1 Spike Plan

> Prepared 2026-07-31. Awaits user confirmation to execute.

## Goal

Build a minimal "Hello World" agent using Anthropic Agent SDK (Python) to validate the Track B architecture before investing in the full RA/PM/Builder lineup.

## Why Agent SDK (from Phase 5 evaluation)

| Requirement | Agent SDK Support |
|------------|------------------|
| Tool/MCP model | Same as Claude Code CLI — no new paradigm to learn |
| Subagent isolation | Built-in — each agent owns its state |
| Hosting (Docker/K8s) | Official hosting guide covers multi-tenant deployment |
| Plugin system | Skills/hooks/MCP loadable as plugins |
| Session persistence | S3/Redis backends for cross-host resume |
| Proactive loop | Custom event loop via `agent.run()` |
| A2A communication | Agent Teams (experimental) or custom message bus |

### Pulse Addendum (2026-08-28) — native A2A coverage expanded

Phase 5 pulse (npm 2.1.246 → 2.1.250, 3 releases) findings relevant to this spike:

- **Cross-session messaging (`SendMessage` / `ListAgents`) now also works on Bedrock, Vertex, Foundry, and when telemetry is disabled** (2.1.248). Earlier 2.1.243 fixed cross-session messages silently turning off in rootless containers. → The spike's A2A evaluation should exercise the native Claude Code `SendMessage` path (not just Agent Teams / custom message bus), including telemetry-disabled.
- **`--restricted` mode / `CLAUDE_CODE_RESTRICTED=1`** (2.1.248): removes built-in code-exec tools, keeps file tools inside the working directory, refuses `bypassPermissions`, ignores user/project/local settings — a hardened tool surface worth evaluating for the runner.
- **`self-hosted-runner --client-label <label>`** (2.1.248): lets a runner register a custom label (default hostname) — useful if the spike later manages multiple runners.
- **Cross-session peer messages collapse to a one-line preview by default** (Ctrl+O expands) in 2.1.247 — UI implication if the spike surfaces peer messages.

→ When user confirms the spike, fold these into `Open Decisions` #1 (A2A scope) and #4 (proactive polling scope): evaluate native A2A under telemetry-disabled and self-hosted runner label.

## Spike Deliverable

A single Python service (port 8201) that:

1. Starts an Agent SDK agent with MCP access to the A2A Hub knowledge store
2. Exposes `POST /research` — accepts a topic, returns structured summary + sources
3. Runs a proactive loop: polls GitHub / A2A Hub / web for new Claude Code releases every 6h
4. Persists state to disk (SQLite, fallback when S3 unavailable)
5. Reports health via `GET /health`

## Evaluation Criteria

| Criterion | Pass Threshold |
|-----------|---------------|
| Startup time | < 3s from cold start |
| First research call | < 30s (includes tool invocation) |
| Proactive loop | Fires on schedule, no missed ticks after 24h |
| State persistence | Agent resumes correctly after restart |
| API surface | All endpoints respond within 5s |
| Memory usage | < 500 MB RSS at rest |

## Timeline (estimated 1-2 days)

- Day 1 AM: Scaffold Agent SDK agent, implement `POST /research`
- Day 1 PM: Add proactive loop + scheduling
- Day 2 AM: Add state persistence (SQLite first, S3 adapter)
- Day 2 PM: Add health checks, logging, Dockerfile, write `decisions.md` entry

## Environment Prerequisites (2026-07-31)

| Item | Status |
|------|--------|
| Python 3.13 | ✅ Available |
| `pip install anthropic` (Agent SDK) | ⏳ Not installed — first spike step |
| FastAPI / Flask | ⏳ To be decided during spike |
| SQLite3 | ✅ Built into Python stdlib |
| Port 8201 | ✅ Available (verified) |
| Docker | ❌ `docker.sock` permission denied on this host |
| GPU | ❌ Not required for this spike |

Note: Docker socket permissions are unavailable on this host. The spike service should run as a direct Python process or via systemd. Containerization can be added later when permissions are available.

## Proposed Package Structure

```
self-development/track-b/
├── agent_service.py          # Main entry: FastAPI app + agent loop
├── agent_config.py           # Agent SDK configuration
├── research_agent.py         # Agent SDK agent definition
├── proactive_loop.py         # Scheduled polling logic
├── persistence.py            # SQLite state persistence
├── requirements.txt          # Dependencies
├── Dockerfile                # (Optional, when Docker available)
└── README.md                 # Quick start
```

## Open Decisions (for user)

1. **Agent SDK version**: Use latest stable or pin to a specific release?
2. **Persistence backend**: SQLite for spike, S3/Redis for production — proceed with SQLite first?
3. **MCP scope**: A2A Hub only, or also local file system MCP servers?
4. **Proactive polling scope**: GitHub releases only, or also `docs.anthropic.com` changelog?

## Follow-up

If the spike passes all criteria, proceed to Phase 2 (full RA agent deployment). If it fails on any criterion, document the issue in `experiments.md` and re-evaluate the framework choice.
