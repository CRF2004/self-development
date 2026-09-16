# Decisions

This file records durable choices for the Claude Code self-development project.

## Purpose

The project should not re-litigate every recurring problem.
When a choice proves useful, write it down here so future sessions can start from the decision instead of rediscovering it.

## Decision template

```md
## YYYY-MM-DD — decision title

### Decision
- 

### Why
- 

### Applies to
- Claude Code / MetaBot / both

### Notes
- 
```

## What belongs here

- the current recovery strategy
- stable hook behavior
- prompt structure that consistently helps
- MetaBot defaults that should stay in place
- maintenance rules that should be preserved across sessions

## Rule

If a future review or experiment shows that a decision is no longer correct, update this file and note the reason.

## 2026-05-12 — bootstrap workflow

### Decision
- Use a small local CLI as the project entry point

### Why
- It makes the markdown workflow operational without adding heavy automation

### Applies to
- both

### Notes
- Start manual and keep scheduling separate

## 2026-05-12 — status bootstrap check

### Decision
- Use status output to prompt real log entry bootstrapping

### Why
- It turns the empty project into an actionable checklist

### Applies to
- both

### Notes
- Prefer actual usage over synthetic examples

## 2026-06-08 — src-layout Python packages: pyproject.toml + pip install -e .

### Decision
- For src-layout packages (src/<package>/), create a pyproject.toml with setuptools.build_meta backend and run pip install -e . rather than relying on PYTHONPATH.

### Why
- PYTHONPATH is fragile across sessions and tool invocations. A proper install resolves all intra-package imports reliably. setuptools.build_meta is the correct backend (setuptools.backends._legacy does not exist).

### Applies to
- both

### Notes
- Applied to portraiture project at cc_dump/portraiture/. This pattern is general-purpose for any src-layout Python project in the workspace.

## 2026-06-17 — Daily advancement skip marker convention

### Decision
- Projects with only qualitative/planning tasks (product specs, research goals) that have no executable code should be excluded from daily advancement rotation via a `.daily-advance-skip` marker file.
- The `daily-task-advance.ts` script should check for this marker in the directory filter, not just in EXCLUDED_DIRS.

### Why
- viora has 13 qualitative product goals in plan.md — it passes the `hasPlan && uncheckedTasks > 0` filter every day but has no actionable code work. This creates daily noise in both the snapshot and the recommendations list.
- personal_website has no plan.md at all — it's already excluded from candidates (line 125 filter). Only cosmetically appears as "❌" in the snapshot, which is acceptable.
- A marker file is more maintainable than hard-coded exclude lists or plan.md content parsing.

### Applies to
- both

### Notes
- Marker file location: `<project-root>/.daily-advance-skip`
- The marker is an empty file. Its presence is the signal.
- Applied to: viora/ (qualitative-only plan), potentially personal_website/ if confirmed to be non-code.
- Corresponding code change: `daily-task-advance.ts` lines 94-98 — add `.daily-advance-skip` detection.

## 2026-06-20 — Correction: viora is not qualitative-only

### Decision
- The previous entry (2026-06-17) cited viora as an example of a "qualitative-only" project. This was **incorrect**.
- In a subsequent session, the user pointed out that viora has 21K lines of real Python/Flask code with 174 existing tests. It was misclassified because its plan.md only contained product goals (not yet structured into code-level phases).
- viora's `.daily-advance-skip` marker has been removed. The skip marker convention itself is still valid for projects that genuinely have no executable code (e.g., pure spec documents).
- Updated workflow from user: when a project's plan.md lacks code-level tasks but the project has real code, propose implementation tasks based on the plan content, ask if feasible, then implement.

### Why
- A project with thousands of lines of code, a working Flask server, frontend, and tests should not be excluded from daily advancement just because its plan.md uses product-language rather than code-level checkbox tasks.
- The `.daily-advance-skip` marker was causing real work to be missed.

### Applies to
- both

### Notes
- viora `.daily-advance-skip` deleted 2026-06-18
- The original decision (skip marker as a concept) remains valid. The error was in how it was applied.

## 2026-08-08 — selfdev.py 自带 check 健康检查命令

### Decision
- selfdev.py 提供 check 子命令: 报告 maintenance 节奏(14d) + review/experiment/decision 日志新鲜度(30d 阈值) + 工具自身语法检查

### Why
- 项目需要一个零依赖、可脚本化的方式来发现过时日志与 overdue 维护, 此前只能人肉读 status 输出

### Applies to
- self-development

### Notes
- 常量 MAINTENANCE_CADENCE_DAYS=14, STALE_THRESHOLD_DAYS=30; 08-08 首跑发现 decisions 已 49d 过时并借此补记本条

## 2026-08-19 — selfdev.py 命令分派清理 — 移除不可达 argparse 兜底

### Decision
- CLI 命令分派完全依赖 argparse 的 required subparsers; 不保留 main() 尾部不可达的 parser.error('Unknown command')/return 2 兜底

### Why
- argparse 对未知/缺失子命令已 exit(2), 尾部兜底分支永远执行不到; 移除可关闭覆盖率盲点并简化 main()
- 保留一个 pragma:no cover 的防御性 return 0, 防止未来新增子命令时 main() 静默返回 None

### Applies to
- selfdev.py main() dispatch

### Notes
- 08-18 并行会话的抽取 next_actions_from_plan/_module_status 去重与本改动无冲突; 45 tests 全过

## 2026-09-11 — selfdev 写入前校验: title 非空 / --recent >= 0

### Decision
- 所有写 journal 命令的 --title 必须非空 (strip 后); status --recent 必须 >= 0

### Why
- argparse required=True 只检查 flag 是否出现, --title '' 会写出 ENTRY_RE 无法解析的 '## <date> — ' 幽灵条目 (count_entries=0 / latest None), 对 status/check/capsule 不可见, 与 08-30 幽灵日期同类

### Applies to
- selfdev.py require_text / non_negative_int; format_* 与 build_parser

### Notes
- 新增 9 个测试 (65→74) 全过, 覆盖 99% 保持
