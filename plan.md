# Self-Development Plan

## Goal

Two parallel tracks:

**Track A — MetaBot self-improvement loop**
Build a durable improvement loop for Claude Code and the MetaBot system that runs on top of it.
The system should get better through normal use instead of depending on occasional manual cleanup.
It should also periodically check the wider Claude / agent ecosystem for improvements that are worth adopting.

**Track B — Local Agent Platform**
Deploy a set of independent, sovereign agents (PM, RA, Builder) as standalone services on the local machine, each on its own port, with Claude Code as a callable tool rather than their runtime identity.

## Current direction

We want four things to improve together:

1. Claude Code sessions should stay resumable and easy to continue.
2. MetaBot should preserve useful state and recover gracefully after interruptions.
3. The project should capture what helped so the next session starts from a better baseline.
4. The system should periodically review newer techniques and decide whether its own prompts, hooks, and assumptions are outdated.

## Principles

- Optimize for continuity first.
- Keep recovery payloads short and stable.
- Favor reliable defaults over clever but fragile automation.
- Record useful lessons only when they are likely to help future sessions.
- Verify changes in real usage, not just in theory.
- Prefer small, proven upgrades over speculative rewrites.
- Treat the system prompt, hooks, and workflow conventions as living parts of the project.

## Roadmap

### Phase 1 — Capture the baseline

- record what currently breaks or slows down Claude Code usage
- record what makes MetaBot sessions hard to resume
- keep notes on config, hooks, and recovery behavior that matter in practice
- establish what is currently considered the default operating model

### Phase 2 — Improve continuity

- refine compact-related behavior
- keep the recovery context small and cache-friendly
- preserve the active objective, blockers, and next action
- make resume behavior predictable after a reset or compaction
- keep the session state useful even when the conversation gets long

### Phase 3 — Improve MetaBot intelligence

- make MetaBot better at remembering useful state
- reduce duplicated effort across sessions
- improve task progression across repeated runs
- make the system more proactive without becoming noisy
- identify which tasks can be automated safely and which should stay manual

### Phase 4 — Make improvements repeatable

- turn useful patterns into stable config or hooks
- document recurring fixes and successful workflows
- keep a short feedback loop for observing, adjusting, and validating
- promote proven behavior into defaults instead of re-deciding it every time

### Phase 5 — Review external progress on a schedule

- periodically browse for newer Claude Code capabilities and related agent tooling
- evaluate whether prompt strategies, memory patterns, hooks, or recovery methods should be updated
- check whether older guidance in this project has become stale
- decide what should be adopted, modified, or ignored
- record each review result so the next review starts from prior findings instead of from scratch

**Phase 5 status:** ✅ Executed 2026-07-15 — Claude Code ecosystem scan completed.
Key finding: Agent SDK (Python/TypeScript) is directly relevant to Track B.
Full review in `review-log.md` under `2026-07-15 — Phase 5 — Claude Code ecosystem scan`.

## Local Agent Platform

### Goal

Deploy a set of independent, long-running agents on the local machine — each occupying its own port as a standalone service. These are **not** Claude Code sub-agents; they are sovereign processes that can be called via API, can maintain their own state, and can invoke Claude Code (or other LLM backends) as a tool when needed.

**Key requirement: Proactive intelligence.** Each agent must exhibit a high degree of autonomous initiative — not merely reacting to API calls, but actively driving its own loop:

- **Proactive web browsing** — autonomously browse the web to learn new techniques, monitor ecosystem changes, fetch documentation, and stay current without being asked.
- **Proactive messaging** — initiate and respond to messages on Feishu/Telegram on their own initiative (push notifications, status reports, raising alerts, asking clarifying questions).
- **A2A (Agent-to-Agent) communication** — agents talk to each other proactively: PM assigns work to Builder without human intervention; RA surfaces findings to PM when relevant; Builder reports completion/failure to PM; agents negotiate, escalate, and coordinate among themselves.

The initial lineup:

- **PM (Project Manager)** — tracks project state, breaks down tasks, assigns work, detects blockers. Proactively polls project state, reaches out to RA for research context, delegates to Builder, and pushes status updates to Feishu.
- **RA (Research Assistant)** — searches, summarizes, evaluates novelty, and maintains a research knowledge base. Proactively browses the web to stay current, pushes interesting findings to PM, and answers inbound research queries from other agents.
- **Builder** — takes assigned tasks, writes/edits code, runs tests, and reports results. Proactively reports progress, asks for clarification when specs are ambiguous, and signals completion or blockage to PM.

Each agent is an independently addressable service (e.g., `localhost:8201/pm`, `localhost:8202/ra`, `localhost:8203/builder`), communicating via a shared message bus or direct HTTP calls. A2A communication is first-class: agents discover each other, route messages, and maintain conversation state.

### Principles

- Each agent owns its own lifecycle and state — no shared memory across agents unless explicitly wired.
- Agents can invoke Claude Code / LLM backends as a capability, not as their identity.
- The framework choice (Dify, LangFlow, OpenAI SDK, self-built) is a design decision to be evaluated, not assumed.
- Agents should be operable via simple HTTP APIs and optionally via Feishu/Telegram.
- Start small: one agent, one port, one useful task — then scale.
- **Proactivity is a core capability, not an afterthought.** Each agent runs its own event loop: poll, decide, act, report. Agents should not sit idle waiting for an HTTP request.
- **A2A communication must be built-in from day one.** Message routing, agent discovery, and conversation state are platform-level concerns, not per-agent ad-hoc wiring.
- **Web browsing is a first-class tool.** Every agent should be able to fetch, read, and summarize web content as part of its autonomous decision loop.
- **Messaging is bidirectional.** Agents push notifications proactively (not just respond to commands), and can receive inbound messages from users and other agents.

### Candidate frameworks

| Option | Pros | Cons |
|---|---|---|
| **Dify** | Visual workflow builder, built-in RAG, app publishing | Heavy, opinionated, may not fit custom agent loops |
| **LangFlow** | Visual, open-source, flexible graph-based flows | Less mature, fewer production deployments |
| **OpenAI SDK + FastAPI** | Maximum control, thin layer, easy to self-host | Build everything yourself (auth, state, scheduling) |
| **Self-built (TypeScript/Python)** | Full control, minimal deps, fits our stack | Highest initial cost, reinventing wheels |
| **LangGraph** | Stateful agent graphs, checkpointing, good for multi-step | Learning curve, LangChain dependency |
| **Claude Code Agent SDK** (Python/TypeScript) | Same agent loop/tools/MCP as Claude Code CLI; built-in subagents, hooks, checkpointing, structured output; first-class A2A support (Agent Teams experimental) | Anthropic-only; Agent Teams still experimental; Python/TS only |

Decision is deferred to a spike phase (see Phase 1 below).

Key evaluation lens for proactivity: can the framework support a long-running event loop (poll-decide-act) natively, or does it assume a request/response model? Does it provide built-in web browsing, message sending, and A2A primitives, or must those be built from scratch?


### Roadmap

#### Phase 1 — Spike & evaluate

- Run a 2-3 day spike to build a minimal "Hello World" agent with at least 2 frameworks (e.g., Dify + OpenAI SDK, plus Agent SDK as a third candidate given Phase 5 findings).
- Evaluate each on: startup time, ease of adding tools, state persistence, API surface, observability, **and support for autonomous loops (poll-decide-act), web browsing tooling, and A2A message routing**.
- Pick one framework as the default, document the decision in `decisions.md`.
- **Note from Phase 5 (2026-07-15):** Anthropic Agent SDK emerged as the leading candidate — same tool/MCP/context model as Claude Code CLI, built-in subagents, and first-class checkpointing. Evaluate it alongside Dify and OpenAI SDK in the spike. If Agent Teams matures, A2A communication becomes built-in rather than custom-wired.
- **Note from Phase 5 pulse check (2026-07-18):** Agent SDK now has a hosting guide (Docker/K8s/multi-tenant), plugin system (skills/hooks/MCP as plugins), and session persistence to S3/Redis — all directly relevant to Track B deployment and state management. Add these to the spike evaluation scope.
- **Note from Phase 5 pulse check (2026-08-15):** Claude Code CLI now has **native cross-session A2A**: `SendMessage` + `ListAgents` (2.1.224+) let sessions message each other on any machine, with inbound routing settings (`crossSessionInbound` / `dialogExpiry`). Also `claude self-hosted-runner` (2.1.224) turns own machines/containers into session hosts. Add both to the spike evaluation scope — evaluate native A2A against a custom-wired message bus before committing to the platform's messaging layer. (Subagent forking is on by default in 2.1.232.)

#### Phase 2 — First agent (RA)

- Deploy the Research Assistant as the first standalone agent.
- It should expose a simple API: `POST /research` with a topic, return a structured summary + sources.
- It can use Claude Code or direct API calls to do the actual research.
- **Proactive loop:** The RA should autonomously browse the web on a schedule (e.g., check for new Claude Code releases, agent framework updates, relevant papers), curate findings, and push interesting results to PM and/or Feishu.
- Run it on a fixed port, keep it alive, and test from Feishu.

#### Phase 3 — Second agent (PM)

- Deploy the Project Manager agent.
- It reads `NOW.md`, `plan.md`, and project state to answer: "What should I work on next?"
- It can spawn tasks to the Builder (or directly to Claude Code) and track completion.
- **Proactive loop:** PM polls project state on a schedule, detects stale tasks or blockers, and pushes status updates to Feishu without being asked.
- **A2A:** PM sends task assignments to Builder and receives completion/failure reports. PM receives research briefs from RA and decides whether to incorporate them into the task queue.

#### Phase 4 — Third agent (Builder)

- Deploy the Builder agent.
- Takes a task spec (e.g., "add a /health endpoint to the RA agent") and executes it.
- Reports success/failure back to PM.
- **Proactive loop:** Builder reports progress autonomously (not just on completion). If blocked (ambiguous spec, missing dependency, test failure), it proactively messages PM with a specific question — not just a silent failure.
- **A2A:** Builder can query RA for context (e.g., "how is this endpoint typically structured?") before implementing, and can ask PM to clarify or reprioritize.

#### Phase 5 — Integration & orchestration

- Wire the three agents together via a lightweight message bus or direct API calls.
- Make them callable from MetaBot (Feishu) and from each other.
- Add basic observability (logs, health checks, maybe a simple dashboard).
- **A2A message protocol:** Define a minimal shared message format so agents can route, reply, and maintain conversation threads across turns.
- **Feishu bidirectional bridge:** Agents push to Feishu proactively; users can also message agents directly via Feishu. The MetaBot coordinator routes inbound messages to the right agent.

### What to watch

- Whether agent state survives restarts gracefully.
- Whether the overhead of running N services is justified vs. using Claude Code sub-agents directly.
- Whether the chosen framework stays easy to modify or becomes a constraint.
- Whether Feishu/Telegram integration feels natural or forced.
- **Proactivity quality** — are agents initiating useful actions, or just busy-waiting? Is the signal-to-noise ratio of autonomous messages acceptable?
- **A2A coherence** — do agent-to-agent conversations stay on-track, or do they loop/degrade? Does message context survive across turns?
- **Web learning effectiveness** — do agents surface genuinely useful findings, or just noise? Is the browse-decide-report loop adding value?
- **Autonomy safety** — can agents trigger destructive actions (code changes, deployments, external API calls) without appropriate guardrails?

## What to watch

- whether sessions resume with enough context
- whether recovery text stays concise
- whether automatic compaction helps or gets in the way
- whether MetaBot keeps improving without manual intervention
- whether config changes remain understandable and maintainable
- whether the project is staying current with newer techniques instead of freezing around older assumptions

## Recurring review task

Run a periodic check for:
- new Claude Code features that affect compaction, hooks, memory, sessions, or recovery
- new agent workflow practices that improve continuity or reliability
- any better way to structure prompts, system instructions, or recovery capsules
- any old technique in this project that should be replaced

The output of that review should be one of three things:
- adopt
- adapt
- ignore

## Next actions

### Track A — MetaBot self-improvement (maintenance mode)

- keep using the system normally and note friction points
- record recurring maintenance checks in `maintenance.md` via `selfdev.py check` (14d cadence; next check ~2026-09-25, last 2026-09-11)
- promote proven patterns into defaults
- schedule or trigger the periodic ecosystem review (Phase 5) as part of normal project maintenance
- record each significant improvement in `experiments.md` and `decisions.md`
- keep this folder as the source of truth for the evolution loop

### Track B — Local Agent Platform

- ⏳ awaiting user confirmation of Track B architecture direction & Phase 1 spike plan (`docs/track-b-spike-plan.md`, prepared 2026-07-31)
- after confirmation: run Phase 1 spike — build a minimal Agent SDK "Hello World" agent on port 8201 (`POST /research`, 6h proactive loop, SQLite persistence, `GET /health`)
- record spike results in `experiments.md`; if all criteria pass, write the framework decision into `decisions.md`
- deploy the RA (Research Assistant) as the first real agent (own port)
- test calling it from Feishu via MetaBot
- then proceed to PM → Builder → orchestration

## Working rule

If something improves future Claude Code sessions or makes MetaBot more capable, it belongs here.
If it is only a temporary fix, keep it out unless it reveals a reusable pattern.
