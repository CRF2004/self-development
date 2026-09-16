# Self-Development for Claude Code

This directory treats Claude Code itself as an evolving project.

The goal is simple:
- make Claude Code easier to use over time
- make MetaBot, which runs on top of Claude Code, steadily more capable
- turn repeated usage into a feedback loop that improves prompts, hooks, workflows, recovery behavior, and system design

## What this project is

This is not a product spec and not a one-off notes folder.
It is a working system for improving the way Claude Code works with this repository and for improving the Claude Code-powered MetaBot experience.

Think of it as a loop with four layers:
1. Claude Code usage patterns
2. MetaBot behavior built on Claude Code
3. A regular review process for new techniques and platform changes
4. The self-improvement loop that records what worked, what broke, and what should change next

## Outcomes we want

- fewer context resets
- better session continuity
- faster recovery after compaction or interruption
- more stable hooks and config
- better task handoff between sessions
- more useful automation in MetaBot without making the system fragile
- a reliable habit of checking whether old assumptions, prompts, and techniques are still the best available

## Working style

When something feels awkward, slow, repetitive, or brittle, capture it here.
When something works especially well, capture that too.

The useful output is not just code or config.
It is a repeatable method that makes future Claude Code sessions better than the previous ones.

## What to record

- pain points during real usage
- settings that improved continuity or cache behavior
- hooks that saved time or preserved state
- recovery patterns after compaction or reset
- MetaBot behaviors that should become default
- ideas that should be tested before becoming permanent
- old assumptions that should be rechecked against newer Claude Code or agent practices
- system prompt or workflow pieces that should be revised because a better pattern now exists

## Regular review loop

This project should not only react to local problems.
It should also periodically look outward.

A recurring task should:
- browse for recent Claude Code / agent / workflow / prompt / memory-related improvements
- evaluate whether they can make Claude Code or MetaBot stronger
- check whether current hooks, recovery logic, and system prompt guidance are outdated
- decide what should be adopted, modified, or ignored

The point is to keep the system current, not frozen.

## How to use this folder

- `index.md` is the fast entry point
- `README.md` explains the project and the operating model
- `plan.md` tracks the current roadmap and next steps
- `review-log.md` records periodic external-tech reviews
- `experiments.md` records tests and outcomes
- `decisions.md` records durable choices
- `maintenance.md` records recurring upkeep
- `context.md` gives a compact orientation for future sessions
- `selfdev.py` is the lightweight utility for status and log entries
- add more files when a topic becomes large enough to deserve its own space

## Quick workflow

Use the utility from this directory:

- `python3 selfdev.py status` — includes NOW.md handoff freshness (the single source of truth)
- `python3 selfdev.py status --recent 3`
- `python3 selfdev.py missing`
- `python3 selfdev.py capsule`
- `python3 selfdev.py check` — maintenance cadence + log/NOW.md-freshness health check
- `python3 selfdev.py review --title "..." --decision adopt --checked "..." --promising "..."`
- `python3 selfdev.py experiment --title "..." --verdict keep --hypothesis "..." --result "..."`
- `python3 selfdev.py decision --title "..." --decision "..." --why "..."`
- `python3 selfdev.py maintenance --title "..." --action "..." --checked "..."`

Keep entries short. If a result becomes durable, promote it from `experiments.md` into `decisions.md`.

If the project is still empty, use `python3 selfdev.py status` first and then add one real review, one experiment, and one decision.

For resume after compaction, `python3 selfdev.py capsule` produces a compact summary.

## Core idea

Claude Code should not just be a tool you use.
It should become a tool that gets better because you used it well.

MetaBot should follow the same rule.
The project should keep turning usage into memory, memory into structure, structure into better future sessions, and external progress into periodic upgrades.


## 服务器停用归档（2026-09-16）

此私有仓库保存服务器 `/mnt/chengrongfeng_private/cc_dump/self-development/` 的代码、设计、决策、复盘和实验记录。原始目录没有 Git 历史，本次建立 main 分支和初始归档提交。原始文件另有本地压缩备份。

### 恢复使用

本项目命令行工具使用 Python 标准库。进入项目目录后运行：

```bash
python selfdev.py status
python selfdev.py capsule
python selfdev.py --help
```

从 `index.md`、`NOW.md` 和 `plan.md` 查看项目入口、当前进度和计划。自动化调度来自原服务器的 Metabot 环境，恢复自动推进时还需重新配置对应定时任务。
