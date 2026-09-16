# Maintenance

This file describes recurring upkeep for the self-development project.

## Regular maintenance tasks

- review whether compact/recovery behavior is still effective
- check whether Claude Code or MetaBot has drifted from the current operating model
- browse for newer techniques that may improve session continuity or automation
- verify that system prompt guidance still matches the project's real needs
- keep the recovery capsule concise and stable
- promote proven behavior into defaults
- remove stale or temporary ideas that no longer help

## Maintenance rule

Maintenance is not cleanup for its own sake.
It is the process of keeping the project aligned with better available methods.

## Suggested cadence

- lightweight check during normal usage when something feels off
- deeper review on a regular schedule
- immediate review when a new Claude Code capability looks relevant

## Success criteria

The project is healthy when:
- Claude Code sessions are easier to resume
- MetaBot needs less manual correction over time
- recent improvements are reviewed and either adopted or consciously rejected
- the docs reflect current practice instead of old assumptions

## 2026-05-13 — bootstrap maintenance

### What was checked
- logs are concise

### What needs attention
- maintenance entries are missing

### Action
- record recurring upkeep checks

### Follow-up
- add the first real maintenance note

## 2026-05-13 — summary workflow check

### What was checked
- recent summary command exists

### What needs attention
- first real maintenance note still pending

### Action
- use status --recent for quick scans

### Follow-up
- add a maintenance entry after real use

## 2026-07-15 — Q3 maintenance check — logs healthy, no pain points

### What was checked
- review-log.md: 11 entries, latest 2026-07-14
- experiments.md: 3 entries, latest 2026-06-08
- decisions.md: 5 entries, latest 2026-06-20
- maintenance.md: 2 entries (last updated 2026-05-13)
- selfdev.py: syntax OK, status/capsule/entry commands all functional

### What needs attention
- Maintenance log had only bootstrap entries from May — this is the first real maintenance entry
- No new pain points or workflow friction observed in recent daily advancement sessions

### Action
- All project files are stable and healthy. Passive observation mode remains appropriate.
- Phase 5 ecosystem review and Track B architecture decision remain as speculative next actions pending user input.

### Follow-up
- Re-check in 2 weeks or when a concrete pain point arises.
- Phase 5 external review is the most substantial next action available — requires user to define scope.

## 2026-07-25 — Q3 maintenance check — logs healthy, passive observation continues

### What was checked
- review-log.md: 13 entries, latest 2026-07-18 (Phase 5 pulse check)
- experiments.md: 3 entries, latest 2026-06-08
- decisions.md: 5 entries, latest 2026-06-20
- maintenance.md: Pre-existing entries healthy, NOW.md current
- context.md: Updated from bootstrap-era content to current maintenance-mode reference
- selfdev.py: syntax OK, status command functional
- plan.md: Track B still has Phase 5 pulse check findings incorporated (Agent SDK hosting/Docker/session persistence)

### What needs attention
- No new pain points or workflow friction observed since last check (July 15)
- Track B still blocked on user architecture confirmation — no code-level work to advance without it
- experiments.md remains thin (3 entries, all from June or earlier) — could use promotion from review-log entries if applicable

### Action
- context.md modernized from bootstrap instructions to current-state reference
- All project files healthy. Project remains in passive observation mode.
- Next meaningful advance requires either: (a) user confirms Track B architecture, or (b) a concrete Claude Code/MetaBot workflow pain point emerges.

### Follow-up
- Next maintenance check: ~2 weeks (2026-08-08) or on next daily advancement session
- experiments.md review opportunity: when a new technique is tested or Phase 5 SDK evaluation produces measurable results

## 2026-08-04 — Q3 maintenance check — Track B env re-verified, spike still pending

### What was checked
- Track B spike env re-check: Python 3.13.5, anthropic SDK NOT installed, fastapi 0.136.1, sqlite3 3.45.3, port 8201 free
- selfdev.py status/missing/capsule all functional; no drift from 2026-07-25 check
- review-log.md 14 entries, experiments.md 4, decisions.md 5, maintenance.md 4; NOW.md current
- docs/track-b-spike-plan.md env prerequisite table still accurate

### What needs attention
- Track B spike cannot start until user confirms open decisions (Agent SDK version, persistence backend, MCP scope, polling scope)
- anthropic SDK not yet installed — first spike step remains blocked on confirmation

### Action
- Re-verified spike prerequisites (2026-08-04); no environmental drift since 2026-08-03
- Refreshed plan.md '## Next actions' section — removed completed bootstrap-era items, aligned Track A to maintenance mode and Track B to the confirmed spike plan
- Project remains in passive observation mode; no code-level work available without user confirmation

### Follow-up
- Start Track B spike on user confirmation; next scheduled maintenance check ~2026-08-11
- Experiments.md is ready for a Phase 5 SDK evaluation entry once the spike runs

## 2026-08-10 — Q3 maintenance check — `selfdev.py check` all green

### What was checked
- Ran `selfdev.py check` (maintenance 14d / logs 30d / tool syntax):
  - maintenance: ok — last check 6d ago (next in 8d)
  - review-log: ok — latest 11d ago
  - experiments: ok — latest 26d ago
  - decisions: ok — latest 2d ago
  - selfdev.py: syntax OK
- docs/track-b-open-decisions.md + track-b-spike-plan.md still current; no drift

### What needs attention
- Nothing stale found by the automated check
- Track B spike still pending user confirmation of the 4 open decisions (README of track-b-open-decisions.md lists recommended defaults — user replying 「全用推荐默认值」 would unblock immediately)

### Action
- Maintenance entry logged; passive observation mode continues
- Re-confirmed: the single highest-value unblock is user confirming Track B open decisions

### Follow-up
- Next scheduled maintenance check ~2026-08-24 (14d cadence); Track B spike starts on user confirmation
- No code-level work available without user confirmation — project healthy

## 2026-08-14 — Q3 maintenance check — `selfdev.py check` all green

### What was checked
- Ran `selfdev.py check` (maintenance 14d / logs 30d / tool syntax):
  - maintenance: ok — last check 4d ago (next in 10d)
  - review-log: ok — latest 15d ago
  - experiments: ok — latest 30d ago
  - decisions: ok — latest 6d ago
  - selfdev.py: syntax OK
- Track B spike prerequisites re-verified:
  - anthropic: NOT installed (spike first step)
  - fastapi: installed (0.136.1)
  - port 8201: free
- 24 pytest tests pass (2026-08-14 复核 ✅)

### What needs attention
- Nothing stale found by the automated check
- Track B spike still pending user confirmation of the 4 open decisions — replying 「全用推荐默认值」 unblocks immediately

### Action
- Maintenance entry logged; passive observation mode continues
- Re-confirmed: single highest-value unblock is user confirming Track B open decisions

### Follow-up
- Next scheduled maintenance check ~2026-08-24 (14d cadence); Track B spike starts on user confirmation
- No code-level work available without user confirmation — project healthy

## 2026-08-19 — Q3 maintenance check — dead-code cleanup, no drift

### What was checked
- selfdev.py 45 tests all pass
- coverage 99% in-process; argparse unreachable fallback removed
- anthropic NOT installed / fastapi 0.136.1 / port 8201 free (no drift)

### What needs attention
- none

### Action
- removed unreachable parser.error fallback in main() (closes known coverage gap)

### Follow-up
- next scheduled check ~2026-09-02

## 2026-08-22 — Light check + print_status bootstrap header fix

### What was checked
- selfdev.py check 全绿 (maintenance 3d / review-log 23d / experiments 7d / decisions 3d; anthropic 未装 / fastapi 0.136.1 / port 8201 空闲)

### What needs attention
- 无新漂移

### Action
- print_status 重构 bootstrap 建议为 suggestions 列表, 修复仅 maintenance 缺失时提示无标题头的问题; 新增 1 test (46 tests 全过, 覆盖 99% 保持)

### Follow-up
- 下次 check ~2026-09-02

## 2026-08-23 — Fix latest_entry out-of-order freshness bug

### What was checked
- selfdev.py check 全绿 (review-log 现报 8d 而非 24d)

### What needs attention
- review-log.md 条目非严格时间序 (08-15 插在 07-30 之前), latest_entry 原按位置取最后一行 → 健康检查新鲜度误报

### Action
- latest_entry 改为取日期最大值 (dt.date.fromisoformat 解析); status/check/capsule 的 latest 现正确; 新增 1 test (out-of-order → max date); 48 tests 全过, 覆盖 99% 保持

### Follow-up
- 下次 check ~2026-09-02

## 2026-09-11 — Check DUE + 空 title 幽灵条目防护 (selfdev.py)

### What was checked
- selfdev.py check: maintenance DUE (19d, 上次 08-23); review ok 7d / experiments ok 8d / decisions NEARING STALE 23d; anthropic 未装 / fastapi 0.136.1 / port 8201 free
- tests 65→74 全过, 覆盖 99% 保持

### What needs attention
- maintenance 已逾期需补记; decisions.md 距 30d 过时阈值 ≤7d

### Action
- 新增 require_text(): 写 journal 的 --title 非空校验 (strip 后), 防 '## <date> — ' 幽灵条目; 新增 non_negative_int(): status --recent 拒绝负数; 本次补记 maintenance

### Follow-up
- 下次 check ~2026-09-25; decisions 若 >30d 补记
