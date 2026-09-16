#!/usr/bin/env python3
"""Small utility for the self-development project.

Commands:
  status
  missing
  capsule
  check
  review
  experiment
  decision
  maintenance
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import tempfile
from pathlib import Path
from textwrap import indent

ROOT = Path(__file__).resolve().parent
FILES = {
    "review": ROOT / "review-log.md",
    "experiment": ROOT / "experiments.md",
    "decision": ROOT / "decisions.md",
    "plan": ROOT / "plan.md",
    "readme": ROOT / "README.md",
    "context": ROOT / "context.md",
    "maintenance": ROOT / "maintenance.md",
    "index": ROOT / "index.md",
    "now": ROOT / "NOW.md",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ENTRY_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s+—\s+(.+?)\s*$")
UPDATED_RE = re.compile(r"^Updated:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)
NEXT_FIELD_RE = re.compile(r"^Next:\s*(.*)$")
NUMBERED_ITEM_RE = re.compile(r"^\d+[.)]\s*(.*)$")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def atomic_write(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` via a same-directory temp file + ``os.replace``.

    ``Path.write_text`` opens the target with mode "w", which truncates it before
    any bytes are written — so an interruption mid-write (crash, SIGKILL, disk
    full) leaves the dated logs empty and every prior entry lost instead of just
    failing the append. Those logs are this project's memory, so write to a
    sibling temp file first and swap it in atomically: readers (and a failed
    write) always see either the complete old file or the complete new one.
    """
    # Unique temp name so two parallel sessions appending at once cannot clobber
    # each other's in-flight file. Same directory => same filesystem => atomic.
    handle_fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=f"{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(handle_fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    except OSError:
        # Never leave a stray temp file behind when the swap fails.
        Path(tmp_name).unlink(missing_ok=True)
        raise


def write_entry(path: Path, entry: str) -> None:
    existing = read_text(path).rstrip()
    if existing:
        atomic_write(path, existing + "\n\n" + entry.rstrip() + "\n")
    else:
        atomic_write(path, entry.rstrip() + "\n")


def count_entries(text: str) -> int:
    return sum(1 for line in text.splitlines() if ENTRY_RE.match(line.strip()))


def latest_entry(text: str) -> str | None:
    """Return the most recent entry header by date (not merely the last line).

    Log files are not guaranteed to be in chronological order — a new entry may
    be inserted into the middle of the file — so track the maximum date instead
    of the last match. Returns "YYYY-MM-DD — title" or None when no entry parses.
    """
    latest: str | None = None
    latest_date: dt.date | None = None
    for line in text.splitlines():
        match = ENTRY_RE.match(line.strip())
        if not match:
            continue
        try:
            date = dt.date.fromisoformat(match.group(1))
        except ValueError:
            date = None
        if date is not None and (latest_date is None or date > latest_date):
            latest_date = date
            latest = f"{match.group(1)} — {match.group(2)}"
    return latest


def collect_entries(text: str) -> list[list[str]]:
    entries: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        if ENTRY_RE.match(line.strip()):
            if current:
                entries.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        entries.append(current)
    return entries


def _block_date(block: list[str]) -> dt.date | None:
    """Parse the entry date from a block's header line; None when not parseable."""
    if not block:
        return None
    match = ENTRY_RE.match(block[0].strip())
    if not match:
        return None
    try:
        return dt.date.fromisoformat(match.group(1))
    except ValueError:
        return None


def recent_blocks(text: str, count: int) -> list[str]:
    blocks = collect_entries(text)
    if count <= 0:
        return []
    # Log files are not guaranteed to be chronological (see latest_entry), so
    # "recent" must mean newest-by-date, not merely last-in-file. Undated blocks
    # sort as oldest so they only surface when few dated entries exist.
    blocks.sort(key=lambda block: _block_date(block) or dt.date.min)
    return ["\n".join(block) for block in blocks[-count:]]


def bullet_lines(values: list[str]) -> str:
    if not values:
        return "- None"
    return "\n".join(f"- {value}" for value in values)


def next_actions_from_plan(plan_text: str) -> list[str]:
    """Extract bullet items under the '## Next actions' heading of plan.md.

    Returns the visible item text without the leading "- " marker, an optional
    "- [ ]"/"- [x]" task-list checkbox, and surrounding whitespace; [] when the
    heading is absent or the text is empty. Shared by `status` and `capsule`.

    Lines are stripped before matching so indented headings still parse, "### "
    sub-sections inside the block are skipped rather than ending capture, while a
    top-level heading ("# " H1 or "## " H2) ends the block so a trailing section
    cannot leak its bullets, and empty bullets (e.g. a bare "-") are dropped.
    """
    if not plan_text:
        return []
    next_actions: list[str] = []
    capture = False
    for raw_line in plan_text.splitlines():
        line = raw_line.strip()
        if line.startswith("## Next actions"):
            capture = True
            continue
        # A new top-level section ends the block: "## " (H2) is the usual
        # boundary, but also stop at "# " (H1) so e.g. a trailing "# Archived"
        # section cannot leak bullets into next-actions. H3+ sub-headings
        # ("### Track A/B") stay inside the block and are skipped below.
        if capture and line.startswith(("# ", "## ")):
            break
        if not capture or line.startswith("#") or not line.startswith("-"):
            continue
        item = line[1:].strip()
        # Strip a "- [ ] task" / "- [x] task" checkbox, but leave other
        # bracket-prefixed items (e.g. "- [ref] note") untouched.
        if len(item) >= 3 and item[0] == "[" and item[2] == "]" and item[1] in (" ", "x", "X"):
            item = item[3:].strip()
        if item:
            next_actions.append(item)
    return next_actions


def next_items_from_now(now_text: str) -> list[str]:
    """Extract the items under NOW.md's ``Next:`` field.

    CLAUDE.md makes NOW.md the single source of truth and its ``Next`` the default
    next step, but the resume capsule used to derive guidance only from plan.md —
    so a post-compact session never saw the actual handoff (``plan.md`` is
    explicitly *not* the live progress panel). Items are returned without their
    numbering ("1." / "2)") or "- " marker; [] when the field is absent or empty.

    Per the handoff template in CLAUDE.md the items are indented, so the block
    ends at the first non-indented line (the next top-level field, e.g.
    ``Blockers:``) and that section's content cannot leak in.
    """
    if not now_text:
        return []
    items: list[str] = []
    capture = False
    for raw_line in now_text.splitlines():
        line = raw_line.strip()
        if not capture:
            match = NEXT_FIELD_RE.match(line)
            if match:
                capture = True
                inline = match.group(1).strip()
                if inline:
                    items.append(inline)
            continue
        if not line:
            continue
        if not raw_line[:1].isspace():
            break
        numbered = NUMBERED_ITEM_RE.match(line)
        if numbered:
            item = numbered.group(1).strip()
        elif line.startswith("-"):
            # Also drops a bare "-" (empty item) rather than keeping the dash.
            item = line[1:].strip()
        else:
            item = line
        if item:
            items.append(item)
    return items


def blocker_from_plan(next_actions: list[str]) -> str | None:
    """Return the first user-blocked item in the plan's Next actions.

    Items awaiting the user (marked with ⏳ / "awaiting user") are what keep a
    maintenance-mode project from advancing; surfacing them in the resume
    capsule tells the next session exactly what to ask the user about.
    """
    for item in next_actions:
        if item.startswith("⏳") or "awaiting user" in item.lower():
            return item
    return None


def today(value: str | None) -> str:
    if value:
        if not DATE_RE.match(value):
            raise SystemExit(f"Invalid date '{value}'. Use YYYY-MM-DD.")
        try:
            dt.date.fromisoformat(value)
        except ValueError:
            raise SystemExit(f"Invalid date '{value}'. Not a real calendar date (e.g. 2026-02-31).")
        return value
    return dt.date.today().isoformat()


def require_text(value: str, label: str) -> str:
    """Reject an empty/whitespace-only required text value, trimming the rest.

    argparse's ``required=True`` only checks that the flag was passed, so
    ``--title ""`` would write a header ("## <date> — ") that ENTRY_RE cannot
    parse — a "ghost entry" invisible to count_entries / latest_entry / check
    (mirrors the ghost-date guard in ``today``). Trailing/leading whitespace is
    trimmed so headers never carry stray edge spaces.
    """
    if not value or not value.strip():
        raise SystemExit(f"Empty {label}. Provide a non-empty value.")
    return value.strip()


def format_review(args: argparse.Namespace) -> str:
    return "\n".join(
        [
            f"## {today(args.date)} — {require_text(args.title, 'title')}",
            "",
            "### What was checked",
            bullet_lines(args.checked),
            "",
            "### What looked promising",
            bullet_lines(args.promising),
            "",
            "### What was not worth changing",
            bullet_lines(args.not_worth),
            "",
            "### Decision",
            f"- {args.decision}",
            "",
            "### Follow-up",
            bullet_lines(args.follow_up),
        ]
    )


def format_experiment(args: argparse.Namespace) -> str:
    return "\n".join(
        [
            f"## {today(args.date)} — {require_text(args.title, 'title')}",
            "",
            "### Hypothesis",
            bullet_lines(args.hypothesis),
            "",
            "### Change made",
            bullet_lines(args.change_made),
            "",
            "### Result",
            bullet_lines(args.result),
            "",
            "### Keep / change / discard",
            f"- {args.verdict}",
            "",
            "### Lesson",
            bullet_lines(args.lesson),
        ]
    )


def format_decision(args: argparse.Namespace) -> str:
    return "\n".join(
        [
            f"## {today(args.date)} — {require_text(args.title, 'title')}",
            "",
            "### Decision",
            # The decision is this entry's whole point, so an empty/whitespace
            # value must be rejected too: argparse only enforces that the flag
            # was passed, and `--decision ""` would otherwise write a recorded
            # but contentless decision ("### Decision\n- ").
            bullet_lines([require_text(args.decision, "decision")]),
            "",
            "### Why",
            bullet_lines(args.why),
            "",
            "### Applies to",
            bullet_lines(args.applies_to),
            "",
            "### Notes",
            bullet_lines(args.notes),
        ]
    )


def format_maintenance(args: argparse.Namespace) -> str:
    return "\n".join(
        [
            f"## {today(args.date)} — {require_text(args.title, 'title')}",
            "",
            "### What was checked",
            bullet_lines(args.checked),
            "",
            "### What needs attention",
            bullet_lines(args.needs_attention),
            "",
            "### Action",
            bullet_lines(args.action),
            "",
            "### Follow-up",
            bullet_lines(args.follow_up),
        ]
    )


def print_status() -> int:
    print("Self-development project status\n")
    print(f"Root: {ROOT}")
    print("\nFiles:")
    # NOW.md leads the list: it is the single source of truth (CLAUDE.md), and a
    # stale/missing handoff is the classic failure mode. Showing its freshness in
    # the primary command means a session running plain `status` sees it too,
    # instead of the signal living only in `check`.
    now_path = FILES["now"]
    now_state = "present" if now_path.exists() else "missing"
    print(f"- NOW.md: {now_state}; {now_handoff_status(read_text(now_path))}")
    static_keys = ["readme", "index", "plan", "context"]
    log_keys = ["review", "experiment", "decision", "maintenance"]
    for key in static_keys + log_keys:
        path = FILES[key]
        state = "present" if path.exists() else "missing"
        if key in log_keys:
            # Entry counts / latest dates only make sense for the dated logs,
            # not for static docs (README/plan/context) which carry no entries.
            text = read_text(path)
            print(f"- {path.name}: {state}; {count_entries(text)} entries")
            latest = latest_entry(text)
            if latest:
                print(indent(f"latest: {latest}", "  "))
        else:
            print(f"- {path.name}: {state}")
    next_actions = next_actions_from_plan(read_text(FILES["plan"]))
    if next_actions:
        print("\nNext actions:")
        for item in next_actions[:5]:
            print(f"- {item}")
        if len(next_actions) > 5:
            print(f"  … (+{len(next_actions) - 5} more — see plan.md '## Next actions')")
    blocker = blocker_from_plan(next_actions)
    if blocker:
        # The primary command should also surface the item gating progress,
        # consistent with the resume capsule (which already reports it).
        print(f"Blocked on: {blocker}")
    suggestions: list[str] = []
    for key, hint in [
        ("review", "review: capture a real tool/prompt review"),
        ("experiment", "experiment: record a change you tried and what happened"),
        ("decision", "decision: promote a proven pattern into a durable rule"),
    ]:
        if count_entries(read_text(FILES[key])) == 0:
            suggestions.append(hint)
    if count_entries(read_text(FILES["maintenance"])) == 0:
        suggestions.append("maintenance: record a recurring upkeep check")
    if suggestions:
        print("\nSuggested bootstrap entries:")
        for suggestion in suggestions:
            print(f"- {suggestion}")
    return 0


def print_summary(count: int) -> int:
    print(f"Recent entries ({count})\n")
    for key in ["review", "experiment", "decision", "maintenance"]:
        text = read_text(FILES[key])
        blocks = recent_blocks(text, count)
        print(f"[{key}]")
        if not blocks:
            print("- None")
            continue
        for block in blocks:
            first_line = block.splitlines()[0]
            # 去掉 "## " 前缀, 与 status 里 latest_entry 的展示风格一致
            if first_line.startswith("## "):
                first_line = first_line[3:]
            print(f"- {first_line}")
        print()
    return 0


def print_missing() -> int:
    print("Missing / thin areas\n")
    for key, label in [
        ("review", "review-log.md"),
        ("experiment", "experiments.md"),
        ("decision", "decisions.md"),
        ("maintenance", "maintenance.md"),
    ]:
        text = read_text(FILES[key])
        entries = count_entries(text)
        if entries == 0:
            print(f"- {label}: no entries yet")
        elif entries == 1:
            print(f"- {label}: only one entry; add one more real example")
        else:
            print(f"- {label}: {entries} entries")
    return 0


# 健康检查相关常量
MAINTENANCE_CADENCE_DAYS = 14  # maintenance 建议节奏 (~2 周)
STALE_THRESHOLD_DAYS = 30  # review/experiment/decision 超过该天数视为过时
STALE_WARN_LEAD_DAYS = 7  # 距过时阈值 ≤ 该天数时提前告警, 留出补记时间


def now_updated_date(text: str) -> dt.date | None:
    """Parse the ``Updated: YYYY-MM-DD`` field from NOW.md; None when absent/invalid.

    NOW.md is the single source of truth for the current handoff (see CLAUDE.md),
    and a stale one silently misleads the next session, so ``check`` reports its
    freshness. Returns None when the field is missing or not a real date.
    """
    if not text:
        return None
    match = UPDATED_RE.search(text)
    if not match:
        return None
    try:
        return dt.date.fromisoformat(match.group(1))
    except ValueError:
        return None


def now_handoff_status(text: str) -> str:
    """One-line freshness summary of the NOW.md handoff.

    NOW.md is the single source of truth (CLAUDE.md), and a stale or missing one
    silently misleads the next session, so both ``check`` and the primary
    ``status`` command surface this. Returns the same wording used by ``check``
    (``ok — updated Nd ago`` / ``STALE — ...`` / ``FUTURE — ...`` for a date ahead
    of today / a prompt to add ``Updated:``).
    """
    updated = now_updated_date(text)
    if updated is None:
        return "no `Updated:` date — add/refresh one so freshness is checkable"
    today = dt.date.today()
    if updated > today:
        # NOW.md is a handoff, not a schedulable log entry: an `Updated:` date in
        # the future cannot be legitimate, and clamping it to 0d would report a
        # broken handoff as "ok — updated 0d ago" indefinitely (log entries may be
        # pre-written, which is why `_entry_age_days` clamps instead).
        return (
            f"FUTURE — Updated {updated.isoformat()} is ahead of today "
            f"({today.isoformat()}) — fix the date"
        )
    age = (today - updated).days
    if age > STALE_THRESHOLD_DAYS:
        return f"STALE — updated {age}d ago (rebuild it per CLAUDE.md)"
    return f"ok — updated {age}d ago"


def _entry_age_days(latest: str | None) -> tuple[dt.date | None, int | None]:
    """从 latest 条目字符串解析日期, 返回 (日期, 距今天数); 无法解析时返回 (None, None)。

    未来日期 (例如预写/排期写入的条目) 按 0 天处理, 避免 check 输出 "-Nd ago" 这类
    负天数造成困惑——未来条目应视为最新鲜, 而不是让健康检查报告一个负数。
    """
    if not latest:
        return None, None
    date_str = latest.split("—")[0].strip()
    try:
        parsed = dt.date.fromisoformat(date_str)
    except ValueError:
        return None, None
    age = (dt.date.today() - parsed).days
    return parsed, max(0, age)


def _port_status(port: int) -> str:
    """Check whether a TCP port is currently free on loopback."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", port))
            return f"port {port}: free"
        except OSError:
            return f"port {port}: IN USE"


def _module_status(module_name: str, missing_msg: str) -> str:
    """Check importability of a module and format a 'installed / NOT installed' line."""
    try:
        module = __import__(module_name, fromlist=["__version__"])
        version = getattr(module, "__version__", "?")
        return f"{module_name}: installed ({version})"
    except ImportError:
        return missing_msg


def env_prereq_lines() -> list[str]:
    """Track B spike prerequisite status (anthropic SDK, fastapi, port 8201).

    Read-only introspection used by `check` so the next session can see at a
    glance whether the spike is ready to start.
    """
    lines: list[str] = [
        _module_status("anthropic", "anthropic: NOT installed (spike first step: pip install anthropic)"),
        _module_status("fastapi", "fastapi: NOT installed"),
    ]
    lines.append(_port_status(8201))
    return lines


def print_check() -> int:
    """轻量健康检查: maintenance 节奏 + 各日志新鲜度 + NOW.md 交接新鲜度 + 工具语法 + Track B spike 前置环境。"""
    today = dt.date.today()
    print("Self-development health check\n")

    # 1) maintenance 节奏
    maint = read_text(FILES["maintenance"])
    _, maint_age = _entry_age_days(latest_entry(maint))
    if maint_age is None:
        print("maintenance: no dated entry — schedule a check")
    elif maint_age >= MAINTENANCE_CADENCE_DAYS:
        print(f"maintenance: DUE — last check {maint_age}d ago "
              f"(cadence {MAINTENANCE_CADENCE_DAYS}d, check now)")
    else:
        next_date = today + dt.timedelta(days=MAINTENANCE_CADENCE_DAYS - maint_age)
        print(f"maintenance: ok — last check {maint_age}d ago (next ~{next_date.isoformat()})")

    # 2) 日志新鲜度
    for key, label in [
        ("review", "review-log"),
        ("experiment", "experiments"),
        ("decision", "decisions"),
    ]:
        _, age = _entry_age_days(latest_entry(read_text(FILES[key])))
        if age is None:
            print(f"{label}: no dated entry")
        elif age > STALE_THRESHOLD_DAYS:
            print(f"{label}: STALE — latest {age}d ago (>{STALE_THRESHOLD_DAYS}d)")
        elif age >= STALE_THRESHOLD_DAYS - STALE_WARN_LEAD_DAYS:
            print(
                f"{label}: NEARING STALE — latest {age}d ago "
                f"(threshold {STALE_THRESHOLD_DAYS}d, ≤{STALE_WARN_LEAD_DAYS}d to go)"
            )
        else:
            print(f"{label}: ok — latest {age}d ago")

    # 3) NOW.md 交接新鲜度 (CLAUDE.md: 过时的 NOW.md 应被重建)
    print(f"now.md: {now_handoff_status(read_text(FILES['now']))}")

    # 4) 工具自身语法
    import py_compile

    try:
        py_compile.compile(str(ROOT / "selfdev.py"), doraise=True)
        print("selfdev.py: syntax OK")
    except py_compile.PyCompileError as exc:
        print(f"selfdev.py: SYNTAX ERROR — {exc}")

    # 5) Track B spike 前置环境 (anthropic SDK / fastapi / port 8201)
    print("\nTrack B spike prerequisites:")
    for line in env_prereq_lines():
        print(f"  {line}")

    return 0


def print_capsule() -> int:
    print("Claude resume capsule\n")
    print(f"project_root: {ROOT.parent}")
    print("state: postcompact")
    print("content_kind: compact_summary\n")
    print("resume_summary:")
    print(f"selfdev: root={ROOT}")
    print(f"selfdev: status=ready")
    for key in ["review", "experiment", "decision", "maintenance"]:
        text = read_text(FILES[key])
        entries = count_entries(text)
        latest = latest_entry(text)
        print(f"selfdev: {key}_entries={entries}")
        if latest:
            print(f"selfdev: {key}_latest={latest}")
    now_next = next_items_from_now(read_text(FILES["now"]))
    if now_next:
        # CLAUDE.md: NOW.md's `Next` is the default next step, and the capsule is
        # what a post-compact session resumes from — plan.md's actions alone left
        # the actual handoff invisible at resume time. One item + a remainder
        # count keeps the capsule compact.
        print(f"selfdev: now_next={now_next[0]}")
        if len(now_next) > 1:
            print(f"selfdev: now_next_more={len(now_next) - 1}")
    next_actions = next_actions_from_plan(read_text(FILES["plan"]))
    blocker = blocker_from_plan(next_actions)
    if next_actions:
        # When a user-confirmation blocker is present it IS the next action;
        # prefer it so the resume capsule points at the item that gates progress.
        print(f"selfdev: next_action={blocker or next_actions[0]}")
    if blocker:
        print(f"selfdev: blocker={blocker}")
    print(f"selfdev: top_commands=status, status --recent 2, missing, capsule, check")
    return 0


def non_negative_int(value: str) -> int:
    """argparse type for a count that must be >= 0.

    Without this, `status --recent -3` silently fell back to the full status
    output instead of telling the user the value was invalid.
    """
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid int value: '{value}'")
    if number < 0:
        raise argparse.ArgumentTypeError(f"expected a value >= 0, got {number}")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="selfdev",
        description="Utility for the self-development project.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Print project status")
    p_status.add_argument(
        "--recent", type=non_negative_int, default=0, help="Show recent entries per log"
    )

    sub.add_parser("missing", help="Show thin or missing areas")
    sub.add_parser("capsule", help="Print a compact resume capsule")
    sub.add_parser(
        "check",
        help="Lightweight health check (maintenance cadence + log/NOW.md freshness)",
    )

    p_review = sub.add_parser("review", help="Append a review entry")
    p_review.add_argument("--date")
    p_review.add_argument("--title", required=True)
    p_review.add_argument("--checked", action="append", default=[])
    p_review.add_argument("--promising", action="append", default=[])
    p_review.add_argument("--not-worth", action="append", dest="not_worth", default=[])
    p_review.add_argument("--decision", required=True, choices=["adopt", "adapt", "ignore"])
    p_review.add_argument("--follow-up", action="append", default=[])

    p_experiment = sub.add_parser("experiment", help="Append an experiment entry")
    p_experiment.add_argument("--date")
    p_experiment.add_argument("--title", required=True)
    p_experiment.add_argument("--hypothesis", action="append", default=[])
    p_experiment.add_argument("--change-made", action="append", dest="change_made", default=[])
    p_experiment.add_argument("--result", action="append", default=[])
    p_experiment.add_argument("--verdict", required=True, choices=["keep", "change", "discard"])
    p_experiment.add_argument("--lesson", action="append", default=[])

    p_decision = sub.add_parser("decision", help="Append a decision entry")
    p_decision.add_argument("--date")
    p_decision.add_argument("--title", required=True)
    p_decision.add_argument("--decision", required=True)
    p_decision.add_argument("--why", action="append", default=[])
    p_decision.add_argument("--applies-to", action="append", dest="applies_to", default=[])
    p_decision.add_argument("--notes", action="append", default=[])

    p_maint = sub.add_parser("maintenance", help="Append a maintenance entry")
    p_maint.add_argument("--date")
    p_maint.add_argument("--title", required=True)
    p_maint.add_argument("--checked", action="append", default=[])
    p_maint.add_argument("--needs-attention", action="append", dest="needs_attention", default=[])
    p_maint.add_argument("--action", action="append", default=[])
    p_maint.add_argument("--follow-up", action="append", default=[])

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "status":
        if args.recent > 0:
            return print_summary(args.recent)
        return print_status()
    if args.command == "missing":
        return print_missing()
    if args.command == "capsule":
        return print_capsule()
    if args.command == "check":
        return print_check()
    if args.command == "review":
        write_entry(FILES["review"], format_review(args))
        return 0
    if args.command == "experiment":
        write_entry(FILES["experiment"], format_experiment(args))
        return 0
    if args.command == "decision":
        write_entry(FILES["decision"], format_decision(args))
        return 0
    if args.command == "maintenance":
        write_entry(FILES["maintenance"], format_maintenance(args))
        return 0

    # 不可达: argparse 的 required subparsers 已拦截未知/缺失子命令 (exit 2)。
    # 保留防御性返回, 避免未来新增子命令时 main() 静默返回 None。
    return 0  # pragma: no cover


if __name__ == "__main__":
    raise SystemExit(main())
