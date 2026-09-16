# Experiments

This file records attempts, results, and lessons from improving Claude Code and MetaBot.

## Purpose

Experiments prevent the project from forgetting why a setting, hook, or workflow exists.
They also make it easier to tell the difference between a good idea and a good idea that only worked once.

## Experiment template

```md
## YYYY-MM-DD — title

### Hypothesis
- 

### Change made
- 

### Result
- 

### Keep / change / discard
- 

### Lesson
- 
```

## What belongs here

- compaction and resume behavior tests
- hook behavior tests
- recovery capsule changes
- prompt or system message revisions
- MetaBot task flow changes
- review-driven updates from newer Claude Code capabilities

## Rule

Keep the writeup short enough that future sessions can scan it quickly.
If an experiment becomes a permanent decision, also record it in `decisions.md`.

## 2026-05-12 — bootstrap workflow

### Hypothesis
- a small CLI will make the project easier to maintain

### Change made
- None

### Result
- status and entry commands are now available

### Keep / change / discard
- keep

### Lesson
- keep the format short and markdown-native

## 2026-05-12 — status bootstrap check

### Hypothesis
- status should reveal thin logs

### Change made
- None

### Result
- it surfaces bootstrap suggestions when logs are sparse

### Keep / change / discard
- keep

### Lesson
- keep status focused on next actions

## 2026-06-08 — Portraiture segmentation tuning

### Hypothesis
- Increasing episode_gap_minutes and lowering topic_shift_similarity_threshold will merge more turns per episode, yielding more replay examples without breaking episode coherence

### Change made
- episode_gap_minutes: 45 -> 120, topic_shift_similarity_threshold: 0.08 -> 0.04 in configs/segmentation/baseline_v1.yaml

### Result
- Replay examples: 9 -> 59 (6.5x). Accuracy differentiated from uniform 55.6% to baseline 66.1% / state-aware 67.8% / refined 69.5%. 40 relabel candidates generated for manual review.

### Keep / change / discard
- keep

### Lesson
- Segmentation parameters are the highest-leverage tuning knobs for replay data scale. Episode merging via time gap + similarity threshold works well. The refinement loop now provides genuine marginal gain (+3.4% over baseline).

## 2026-07-15 — Phase 5 — Agent SDK evaluation for Track B

### Hypothesis
- Anthropic Agent SDK (Python/TypeScript) can serve as the primary framework for Track B's Local Agent Platform, replacing the planned Dify/LangFlow spike

### Change made
- Conducted Phase 5 ecosystem scan: evaluated Agent SDK, Agent Teams, Channels, checkpointing, and related Claude Code tooling
- Pulse check (2026-07-18): reviewed Agent SDK hosting guide (Docker/K8s), plugin system (skills/hooks/MCP as plugins), session persistence (S3/Redis) in versions 2.1.210-212
- Compared against Dify, LangFlow, OpenAI SDK+FastAPI, LangGraph, and self-built options using the Phase 1 spike evaluation criteria

### Result
- Agent SDK emerged as the leading candidate: same tool/MCP/context model as Claude Code CLI, built-in subagents with isolated state, checkpointing, structured outputs
- Hosting guide (Docker/K8s/multi-tenant) directly maps to Track B deployment requirements
- Plugin system reduces Track B integration complexity by standardizing skills/hooks/MCP loading
- Session persistence (S3/Redis) enables cross-host agent state resume — a Track B requirement
- Dify/LangFlow spike no longer needed; SDK covers same capabilities with tighter Claude Code integration
- The SDK hosting/plugin/persistence features, not just the agent loop, were the decisive advantages over alternative frameworks

### Keep / change / discard
- keep

### Lesson
- Framework evaluation must check for production-readiness features (hosting, state persistence, plugin loading), not just API ergonomics. Agent SDK won on deployment infrastructure, not agent loop quality.
- Follow-up pulse checks 3 days after a major scan captured rapidly evolving SDK capabilities that the initial scan missed. Schedule pulse checks after all major ecosystem scans.

## 2026-08-15 — Expand selfdev.py CLI test coverage 50%→96%

### Hypothesis
- The CLI entry points (build_parser/main/status/capsule/check) had no direct test coverage, leaving dispatch and formatting logic unguarded.

### Change made
- Added 14 tests in tests/test_selfdev.py covering build_parser subcommands, main() dispatch for status/missing/capsule/check/review/experiment/decision/maintenance, print_status next-actions rendering, print_capsule with next_action, and print_check DUE/STALE/ok branches.

### Result
- selfdev.py coverage 50%→96%; tests 24→38 all pass; real CLI check/status still work (smoke tested).

### Keep / change / discard
- keep

### Lesson
- argparse parser + dispatch + status/capsule formatters are cheap to cover with monkeypatched FILES temp files; only the anthropic-installed and py_compile-error branches remain untested.

## 2026-09-03 — selfdev.py next_actions_from_plan H1 section-boundary fix

### Hypothesis
- a trailing top-level H1 section (e.g. # Archived) after ## Next actions leaked its bullets into status/capsule next-actions, because heading lines were skipped rather than treated as block boundaries

### Change made
- next_actions_from_plan now ends capture at any top-level heading (# H1 as well as ## H2); H3+ sub-sections (e.g. ### Track A/B) inside the block stay skipped, not boundary-ending
- added regression tests: H1 section no longer leaks; empty / no-heading text returns []
- doc refresh: README quick workflow and selfdev.py module docstring now list the check subcommand

### Result
- 64 pytest tests pass, coverage 99% maintained; real plan.md parse unchanged (12 next actions, the Track B blocker still surfaced)

### Keep / change / discard
- keep

### Lesson
- section parsing should treat any heading at the same or higher level as the captured section as a boundary; skipping all heading lines is not enough and lets a following top-level section leak in

## 2026-09-11 — check 新增 NOW.md 交接新鲜度

### Hypothesis
- check 只查 maintenance 节奏与 journal 日志新鲜度, 会漏报过时的 NOW.md (CLAUDE.md 唯一事实来源)

### Change made
- 新增 now_updated_date() 解析 NOW.md 的 Updated: 字段; check 增加 now.md ok/STALE/缺字段三态输出; FILES 新增 now

### Result
- 78 tests 全过, 覆盖 99% 保持; check 实测 now.md: ok — updated 0d ago

### Keep / change / discard
- keep

### Lesson
- 接力棒文件的过时检测应与日志新鲜度同等纳入健康检查

## 2026-09-12 — status 增加 NOW.md 交接新鲜度 (抽取共享助手)

### Hypothesis
- NOW.md 是 CLAUDE.md 的唯一事实来源, 但只有 check 报告其新鲜度; 只用 status 的会话看不到过时/缺失的接力棒

### Change made
- 抽取 now_handoff_status(text) 助手 (原 check 第 3 段内联逻辑), check 改用它保持输出逐字不变; print_status 的 Files 块首行新增 NOW.md 行 (present/missing + ok/STALE/无 Updated 日期)

### Result
- 78→82 tests 全过, 覆盖 99% 保持; check 输出与重构前逐字一致; status 现显示 '- NOW.md: present; ok — updated 1d ago'; 拆分不清空 (无 'no such file' 崩溃)

### Keep / change / discard
- keep

### Lesson
- 同一信号若埋在二级命令, 用户最常用的命令会漏看; 抽取共享助手可让两处输出保持一致且消除重复

## 2026-09-13 — NOW.md 未来 Updated 日期告警

### Hypothesis
- now_handoff_status 对未来的 Updated 日期用 max(0) 钳制为 0d, 会把损坏的接力棒长期报成 ok — updated 0d ago (日志条目可预写故钳制合理, 但 NOW.md 是交接棒, 未来日期必然错误)

### Change made
- now_handoff_status 在 age 计算前新增 updated > today 分支, 输出 FUTURE — Updated <date> is ahead of today (<today>) — fix the date; 新增 3 测试 (助手边界 / status / check)

### Result
- 85→88 tests 全过, 覆盖 99% 保持 (仅剩 __main__ 守卫)

### Keep / change / discard
- keep

### Lesson
- 只对日志条目成立的钳制假设不应默认套用到交接棒文件; 不同语义的输入需要各自的校验
