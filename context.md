# Context

This file keeps a compact description of the project so future sessions can orient quickly.

## The project in one sentence

Treat Claude Code as a system that should continuously improve itself, and treat MetaBot as a Claude Code-powered project that should become more capable over time.

## Why this exists

- long sessions can lose continuity
- older assumptions can become stale
- good workflows should be captured instead of rediscovered
- MetaBot should get smarter through repeated use, not just through one-off fixes
- newer Claude Code capabilities may outperform older prompts, hooks, or recovery strategies

## Operating model

1. Use Claude Code normally.
2. Watch for friction, repetition, or broken continuity.
3. Capture useful lessons.
4. Review newer techniques periodically.
5. Update the project when a better method appears.

## Current state (2026-09-13)

- **Phase 1–5**: All completed
- **Track A (MetaBot self-improvement)**: Maintenance mode — selfdev.py CLI (status/check/capsule/entry commands), 88 pytest tests, 99% coverage
- **Track B (Local Agent Platform)**: Design complete, framework evaluated (Agent SDK recommended), awaiting user confirmation to begin Phase 1 spike
- **Log health**: review-log.md (22 entries), experiments.md (9), decisions.md (8), maintenance.md (11)
- **Last scan**: Phase 5 full scan 2026-07-15; latest pulse 2026-09-04 (npm 2.1.260, decision: adapt)
- **Next maintenance check**: ~2026-09-25 (`selfdev.py check`, last check 2026-09-11)

## Current priority

Maintain passive observation. No active pain points or workflow regressions. The next substantial action is Track B architecture confirmation from the user.

## Quick reference

- `selfdev.py status` — full project view (NOW.md handoff freshness, entry counts per log file, latest entries, next actions)
- `selfdev.py status --recent N` — fast scan of newest N entries
- `selfdev.py missing` — spot thin areas quickly (logs with few entries)
- `selfdev.py capsule` — compact resume summary for post-compact orientation
- `selfdev.py check` — health check: maintenance cadence (14d) + log/NOW.md freshness (30d) + self syntax + Track B spike env
- `plan.md` — roadmap (Track A + Track B), candidate framework evaluation
- `review-log.md` — periodic external-tech reviews (22 entries)
- `decisions.md` — durable choices (8 entries)
- `experiments.md` — tested changes (7 entries)
- `maintenance.md` — recurring upkeep (11 entries)
