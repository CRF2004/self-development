"""
Tests for selfdev.py — the project's own utility for recording
reviews / experiments / decisions / maintenance entries.

Covers the entry-splitting helpers and the `status --recent` display
format (regression for the "## " prefix leak).
"""

import argparse
import datetime as dt
import importlib.util
import os
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("selfdev", _ROOT / "selfdev.py")
selfdev = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(selfdev)

SAMPLE = """\
## 2026-07-01 — First entry

### What was checked
- a

## 2026-07-15 — Second entry

### What was checked
- b
"""


def test_count_entries():
    assert selfdev.count_entries(SAMPLE) == 2


def test_latest_entry():
    assert selfdev.latest_entry(SAMPLE) == "2026-07-15 — Second entry"


def test_latest_entry_skips_invalid_calendar_dates():
    """A header with a non-existent calendar date (e.g. 2026-02-31) is skipped,
    not treated as latest and not a crash."""
    sample = "## 2026-02-31 — bad date\n\n## 2026-08-01 — good\n"
    assert selfdev.latest_entry(sample) == "2026-08-01 — good"


def test_latest_entry_returns_max_date_even_when_out_of_order():
    """latest_entry must pick the newest date, not the last line in the file."""
    sample = """\
## 2026-07-15 — Middle entry

### What was checked
- a

## 2026-08-01 — Newest entry

### What was checked
- b

## 2026-07-01 — Oldest entry

### What was checked
- c
"""
    assert selfdev.latest_entry(sample) == "2026-08-01 — Newest entry"


def test_collect_entries_splits_on_headers():
    blocks = selfdev.collect_entries(SAMPLE)
    assert len(blocks) == 2
    assert blocks[0][0].startswith("## 2026-07-01")
    assert blocks[1][0].startswith("## 2026-07-15")


def test_recent_blocks_returns_last_n():
    blocks = selfdev.recent_blocks(SAMPLE, 1)
    assert len(blocks) == 1
    assert blocks[0].startswith("## 2026-07-15")


def test_recent_blocks_newest_by_date_when_out_of_order():
    """recent_blocks must pick the N newest by date, not the last N in file order.

    Logs (e.g. review-log.md) are not guaranteed chronological, so "recent"
    must be date-based to stay consistent with latest_entry.
    """
    sample = """\
## 2026-07-15 — Middle entry

### What was checked
- a

## 2026-08-01 — Newest entry

### What was checked
- b

## 2026-07-01 — Oldest entry

### What was checked
- c
"""
    blocks = selfdev.recent_blocks(sample, 2)
    assert len(blocks) == 2
    assert blocks[0].startswith("## 2026-07-15")  # middle by date
    assert blocks[1].startswith("## 2026-08-01")  # newest (not last in file)
    # With count=1, the newest-by-date entry wins even though it sits mid-file.
    assert selfdev.recent_blocks(sample, 1)[0].startswith("## 2026-08-01")


def test_block_date_edge_cases():
    """_block_date returns None for empty/undated/invalid-date blocks instead of crashing."""
    assert selfdev._block_date([]) is None
    assert selfdev._block_date(["not a header"]) is None
    assert selfdev._block_date(["## 2026-02-31 — bad date"]) is None
    assert selfdev._block_date(["## 2026-08-01 — good"]) == dt.date(2026, 8, 1)


def test_print_summary_strips_header_prefix(capsys):
    """status --recent must print entries without the '## ' markdown prefix."""
    selfdev.FILES["review"] = _ROOT / "tests" / "_fixture_review.md"
    Path(selfdev.FILES["review"]).write_text(SAMPLE, encoding="utf-8")
    try:
        selfdev.print_summary(2)
        out = capsys.readouterr().out
        assert "## 2026-07-01" not in out
        assert "2026-07-15 — Second entry" in out
    finally:
        Path(selfdev.FILES["review"]).unlink(missing_ok=True)


def test_entry_age_days_parses_latest():
    parsed, age = selfdev._entry_age_days("2026-07-15 — Second entry")
    assert parsed == dt.date(2026, 7, 15)
    assert age == (dt.date.today() - parsed).days
    assert age >= 0


def test_entry_age_days_handles_malformed():
    assert selfdev._entry_age_days(None) == (None, None)
    assert selfdev._entry_age_days("not-a-date — entry") == (None, None)
    assert selfdev._entry_age_days("") == (None, None)


def test_entry_age_days_clamps_future_dates():
    """A future-dated (pre-scheduled) entry is treated as 0 days old, not negative.

    This keeps `check` from reporting confusing negative ages like "-3d ago".
    """
    future = (dt.date.today() + dt.timedelta(days=3)).isoformat()
    parsed, age = selfdev._entry_age_days(f"{future} — scheduled entry")
    assert parsed == dt.date.fromisoformat(future)
    assert age == 0


def test_print_check_reports_no_dated_entries(capsys):
    """With no logs present, check must report missing entries, not crash."""
    for key in ("maintenance", "review", "experiment", "decision"):
        selfdev.FILES[key] = _ROOT / "tests" / f"_fixture_{key}.md"
    try:
        assert selfdev.print_check() == 0
        out = capsys.readouterr().out
        assert "Self-development health check" in out
        assert "no dated entry" in out
    finally:
        for key in ("maintenance", "review", "experiment", "decision"):
            Path(selfdev.FILES[key]).unlink(missing_ok=True)


def test_print_check_reports_spike_prereqs(capsys):
    """check must surface the Track B spike prerequisite section."""
    for key in ("maintenance", "review", "experiment", "decision"):
        selfdev.FILES[key] = _ROOT / "tests" / f"_fixture_{key}.md"
    try:
        selfdev.print_check()
        out = capsys.readouterr().out
        assert "Track B spike prerequisites:" in out
        assert "anthropic:" in out
        assert "fastapi:" in out
        assert "port 8201:" in out
    finally:
        for key in ("maintenance", "review", "experiment", "decision"):
            Path(selfdev.FILES[key]).unlink(missing_ok=True)


def test_env_prereq_lines_shape():
    """env_prereq_lines always reports the three prerequisites."""
    lines = selfdev.env_prereq_lines()
    assert len(lines) == 3
    assert lines[0].startswith("anthropic: ")
    assert lines[1].startswith("fastapi: ")
    assert lines[2].startswith("port 8201: ")


def test_port_status_formats():
    status = selfdev._port_status(8201)
    assert status.startswith("port 8201: ") and status.endswith(("free", "IN USE"))


# ── CLI parser + dispatch (coverage: build_parser / main / status / capsule) ─

def _patch_files(monkeypatch, tmp_path):
    """Point selfdev.FILES at temp files so CLI commands don't touch the repo."""
    for key in ("readme", "index", "plan", "context", "review",
                "experiment", "decision", "maintenance", "now"):
        monkeypatch.setitem(selfdev.FILES, key, tmp_path / f"{key}.md")
    return tmp_path


def test_build_parser_subcommands():
    p = selfdev.build_parser()
    ns = p.parse_args(["status"])
    assert ns.command == "status" and ns.recent == 0
    ns = p.parse_args(["status", "--recent", "2"])
    assert ns.recent == 2
    assert p.parse_args(["missing"]).command == "missing"
    assert p.parse_args(["capsule"]).command == "capsule"
    assert p.parse_args(["check"]).command == "check"
    ns = p.parse_args(["review", "--title", "t", "--decision", "adopt"])
    assert ns.command == "review" and ns.title == "t" and ns.decision == "adopt"


def test_build_parser_requires_required_args():
    with pytest.raises(SystemExit):
        selfdev.build_parser().parse_args(["review"])  # missing --title/--decision


def test_main_status_dispatch(monkeypatch, tmp_path, capsys):
    _patch_files(monkeypatch, tmp_path)
    assert selfdev.main(["status"]) == 0
    out = capsys.readouterr().out
    assert "Self-development project status" in out
    assert "entries" in out


def test_main_status_recent_dispatch(monkeypatch, tmp_path, capsys):
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "review.md").write_text(SAMPLE, encoding="utf-8")
    assert selfdev.main(["status", "--recent", "1"]) == 0
    out = capsys.readouterr().out
    assert "2026-07-15 — Second entry" in out
    assert "## 2026-07-15" not in out


def test_main_missing_and_capsule_dispatch(monkeypatch, tmp_path, capsys):
    _patch_files(monkeypatch, tmp_path)
    assert selfdev.main(["missing"]) == 0
    assert "no entries yet" in capsys.readouterr().out
    assert selfdev.main(["capsule"]) == 0
    out = capsys.readouterr().out
    assert "Claude resume capsule" in out
    assert "selfdev: review_entries=0" in out


def test_main_write_commands_append(monkeypatch, tmp_path):
    _patch_files(monkeypatch, tmp_path)
    assert selfdev.main(["review", "--title", "t", "--decision", "adopt"]) == 0
    assert "t" in (tmp_path / "review.md").read_text(encoding="utf-8")
    assert selfdev.main(["experiment", "--title", "e", "--verdict", "keep"]) == 0
    assert "e" in (tmp_path / "experiment.md").read_text(encoding="utf-8")
    assert selfdev.main(["decision", "--title", "d", "--decision", "x"]) == 0
    assert "d" in (tmp_path / "decision.md").read_text(encoding="utf-8")


def test_main_no_command_raises():
    with pytest.raises(SystemExit):
        selfdev.main([])


def test_print_status_shows_next_actions(monkeypatch, tmp_path, capsys):
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "plan.md").write_text(
        "## Next actions\n- do the thing\n- another\n\n## Other\n", encoding="utf-8")
    assert selfdev.print_status() == 0
    out = capsys.readouterr().out
    assert "Next actions:" in out
    assert "- do the thing" in out
    assert "Suggested bootstrap entries:" in out


def test_print_status_truncation_note_when_many_next_actions(monkeypatch, tmp_path, capsys):
    """Status shows the first 5 Next actions and a (+N more) note when truncated."""
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "plan.md").write_text(
        "## Next actions\n"
        + "".join(f"- item {i}\n" for i in range(1, 9))
        + "\n## Other\n",
        encoding="utf-8")
    assert selfdev.print_status() == 0
    out = capsys.readouterr().out
    # first five are listed, the remaining three are summarized, not dropped silently
    assert "- item 1" in out and "- item 5" in out
    assert "- item 6" not in out
    assert "… (+3 more — see plan.md '## Next actions')" in out


def test_print_status_bootstrap_header_when_only_maintenance_missing(monkeypatch, tmp_path, capsys):
    """Only maintenance empty → header + maintenance line, without other three hints."""
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "review.md").write_text("## 2026-08-01 — r\n\n### What was checked\n- a\n", encoding="utf-8")
    (tmp_path / "experiment.md").write_text("## 2026-08-01 — e\n\n### Hypothesis\n- a\n", encoding="utf-8")
    (tmp_path / "decision.md").write_text("## 2026-08-01 — d\n\n### Decision\n- a\n", encoding="utf-8")
    assert selfdev.print_status() == 0
    out = capsys.readouterr().out
    assert "Suggested bootstrap entries:" in out
    assert "- maintenance: record a recurring upkeep check" in out
    assert "review: capture a real tool/prompt review" not in out
    assert "experiment: record a change you tried and what happened" not in out
    assert "decision: promote a proven pattern into a durable rule" not in out


def test_main_check_dispatch(monkeypatch, tmp_path, capsys):
    _patch_files(monkeypatch, tmp_path)
    assert selfdev.main(["check"]) == 0
    out = capsys.readouterr().out
    assert "Self-development health check" in out
    assert "Track B spike prerequisites:" in out


def test_print_check_maintenance_due(monkeypatch, tmp_path, capsys):
    _patch_files(monkeypatch, tmp_path)
    old = (dt.date.today() - dt.timedelta(days=30)).isoformat()
    (tmp_path / "maintenance.md").write_text(
        f"## {old} — old entry\n\n### What was checked\n- a\n", encoding="utf-8")
    assert selfdev.print_check() == 0
    out = capsys.readouterr().out
    assert "maintenance: DUE" in out
    # When overdue the actionable instruction is "check now", not a confusing
    # "next ~<today>" projection (the check is already past due).
    assert "check now" in out
    assert "next ~" not in out.split("maintenance: DUE")[1]


def test_print_check_maintenance_shows_next_date(monkeypatch, tmp_path, capsys):
    """maintenance ok line projects the concrete next-due date, not just a day count."""
    _patch_files(monkeypatch, tmp_path)
    recent = (dt.date.today() - dt.timedelta(days=4)).isoformat()
    (tmp_path / "maintenance.md").write_text(
        f"## {recent} — recent maintenance\n\n### What was checked\n- a\n", encoding="utf-8")
    assert selfdev.print_check() == 0
    out = capsys.readouterr().out
    next_date = dt.date.today() + dt.timedelta(days=selfdev.MAINTENANCE_CADENCE_DAYS - 4)
    assert f"next ~{next_date.isoformat()}" in out


def test_print_check_log_stale(monkeypatch, tmp_path, capsys):
    _patch_files(monkeypatch, tmp_path)
    old = (dt.date.today() - dt.timedelta(days=45)).isoformat()
    (tmp_path / "review.md").write_text(
        f"## {old} — stale review\n\n### What was checked\n- a\n", encoding="utf-8")
    assert selfdev.print_check() == 0
    out = capsys.readouterr().out
    assert "review-log: STALE" in out


def test_print_check_log_nearing_stale(monkeypatch, tmp_path, capsys):
    """Within STALE_WARN_LEAD_DAYS of threshold → NEARING STALE warning, not ok."""
    _patch_files(monkeypatch, tmp_path)
    near = (dt.date.today() - dt.timedelta(
        days=selfdev.STALE_THRESHOLD_DAYS - selfdev.STALE_WARN_LEAD_DAYS)).isoformat()
    (tmp_path / "review.md").write_text(
        f"## {near} — nearing review\n\n### What was checked\n- a\n", encoding="utf-8")
    assert selfdev.print_check() == 0
    out = capsys.readouterr().out
    assert "review-log: NEARING STALE" in out


def test_main_capsule_with_next_action(monkeypatch, tmp_path, capsys):
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "plan.md").write_text(
        "## Next actions\n- unblock the spike\n\n## Other\n", encoding="utf-8")
    assert selfdev.main(["capsule"]) == 0
    out = capsys.readouterr().out
    assert "selfdev: next_action=unblock the spike" in out
    assert "selfdev: blocker=" not in out  # no ⏳/awaiting item → no blocker line


def test_main_capsule_reports_blocker(monkeypatch, tmp_path, capsys):
    """Capsule surfaces the first user-blocked item (⏳/awaiting) for resume."""
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "plan.md").write_text(
        "## Next actions\n"
        "- do the thing\n"
        "- ⏳ awaiting user confirmation of the spike\n\n"
        "## Other\n", encoding="utf-8")
    assert selfdev.main(["capsule"]) == 0
    out = capsys.readouterr().out
    assert "selfdev: blocker=⏳ awaiting user confirmation of the spike" in out


def test_print_status_reports_blocker(monkeypatch, tmp_path, capsys):
    """status surfaces the first user-blocked item (⏳/awaiting), matching capsule."""
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "plan.md").write_text(
        "## Next actions\n"
        "- keep using the system normally\n"
        "- ⏳ awaiting user confirmation of the spike\n\n"
        "## Other\n", encoding="utf-8")
    assert selfdev.print_status() == 0
    out = capsys.readouterr().out
    assert "Blocked on: ⏳ awaiting user confirmation of the spike" in out


def test_print_status_no_blocker_line_when_none(monkeypatch, tmp_path, capsys):
    """status emits no 'Blocked on:' line when the plan has no ⏳/awaiting item."""
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "plan.md").write_text(
        "## Next actions\n- do the thing\n\n## Other\n", encoding="utf-8")
    assert selfdev.print_status() == 0
    out = capsys.readouterr().out
    assert "Blocked on:" not in out


def test_main_capsule_next_action_prefers_blocker(monkeypatch, tmp_path, capsys):
    """When a ⏳ blocker appears later in the list, capsule's next_action should
    point at it (the item gating progress) rather than the first routine bullet."""
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "plan.md").write_text(
        "## Next actions\n"
        "- keep using the system normally\n"
        "- ⏳ awaiting user confirmation of the spike\n\n"
        "## Other\n", encoding="utf-8")
    assert selfdev.main(["capsule"]) == 0
    out = capsys.readouterr().out
    assert "selfdev: next_action=⏳ awaiting user confirmation of the spike" in out
    assert "selfdev: blocker=⏳ awaiting user confirmation of the spike" in out


def test_print_check_ok_branches(monkeypatch, tmp_path, capsys):
    _patch_files(monkeypatch, tmp_path)
    recent = (dt.date.today() - dt.timedelta(days=2)).isoformat()
    (tmp_path / "maintenance.md").write_text(
        f"## {recent} — recent maintenance\n\n### What was checked\n- a\n", encoding="utf-8")
    (tmp_path / "review.md").write_text(
        f"## {recent} — recent review\n\n### What was checked\n- a\n", encoding="utf-8")
    assert selfdev.print_check() == 0
    out = capsys.readouterr().out
    assert "maintenance: ok" in out
    assert "review-log: ok" in out


def test_main_maintenance_write_dispatch(monkeypatch, tmp_path):
    _patch_files(monkeypatch, tmp_path)
    assert selfdev.main(["maintenance", "--title", "m"]) == 0
    assert "m" in (tmp_path / "maintenance.md").read_text(encoding="utf-8")


# ── Entry-format functions (core write contract) ─────────────────────────────

def _mk_args(**overrides):
    """Build a minimal argparse.Namespace with the given overrides."""
    ns = argparse.Namespace()
    for key, value in overrides.items():
        setattr(ns, key, value)
    return ns


def test_bullet_lines_empty():
    assert selfdev.bullet_lines([]) == "- None"


def test_bullet_lines_values():
    assert selfdev.bullet_lines(["a", "b"]) == "- a\n- b"


def test_format_review_sections():
    args = _mk_args(date="2026-08-11", title="A review", checked=["x"],
                    promising=[], not_worth=[], decision="adopt", follow_up=[])
    out = selfdev.format_review(args)
    assert out.startswith("## 2026-08-11 — A review")
    assert "### What was checked\n- x" in out
    assert "### Decision\n- adopt" in out
    assert "### Follow-up\n- None" in out


def test_format_experiment_sections():
    args = _mk_args(date="2026-08-11", title="An experiment", hypothesis=["h"],
                    change_made=[], result=[], verdict="keep", lesson=[])
    out = selfdev.format_experiment(args)
    assert out.startswith("## 2026-08-11 — An experiment")
    assert "### Hypothesis\n- h" in out
    assert "### Keep / change / discard\n- keep" in out


def test_format_decision_sections():
    args = _mk_args(date="2026-08-11", title="A decision", decision="do it",
                    why=["why1"], applies_to=[], notes=[])
    out = selfdev.format_decision(args)
    assert out.startswith("## 2026-08-11 — A decision")
    assert "### Decision\n- do it" in out
    assert "### Why\n- why1" in out


def test_format_maintenance_sections():
    args = _mk_args(date="2026-08-11", title="A check", checked=["c"],
                    needs_attention=[], action=[], follow_up=[])
    out = selfdev.format_maintenance(args)
    assert out.startswith("## 2026-08-11 — A check")
    assert "### What was checked\n- c" in out
    assert "### Follow-up\n- None" in out


def test_write_entry_appends_to_existing(tmp_path):
    p = tmp_path / "log.md"
    p.write_text("## 2026-08-01 — First\n", encoding="utf-8")
    selfdev.write_entry(p, "## 2026-08-11 — Second\n")
    text = p.read_text(encoding="utf-8")
    assert text.startswith("## 2026-08-01 — First\n\n")
    assert "## 2026-08-11 — Second" in text


def test_write_entry_creates_new_file(tmp_path):
    p = tmp_path / "log.md"
    selfdev.write_entry(p, "## 2026-08-11 — First\n")
    assert p.read_text(encoding="utf-8").startswith("## 2026-08-11 — First")


def test_write_entry_swaps_in_same_dir_temp_file(monkeypatch, tmp_path):
    """The append must go through a sibling temp file + os.replace.

    Atomicity requires the temp file to live in the target's directory (same
    filesystem) and to be consumed by the replace, so no stray file is left."""
    p = tmp_path / "log.md"
    p.write_text("## 2026-08-01 — First\n", encoding="utf-8")
    seen: dict[str, Path] = {}
    real_replace = os.replace

    def capture(src, dst):
        seen["src"] = Path(src)
        seen["dst"] = Path(dst)
        real_replace(src, dst)

    monkeypatch.setattr(os, "replace", capture)
    selfdev.write_entry(p, "## 2026-08-11 — Second\n")

    assert seen["dst"] == p
    assert seen["src"].parent == p.parent        # same dir => atomic swap
    assert not seen["src"].exists()              # temp consumed by replace
    assert [f.name for f in tmp_path.iterdir()] == ["log.md"]


def test_write_entry_is_atomic_on_failed_swap(monkeypatch, tmp_path):
    """A failed write must leave the existing journal intact, not truncated.

    Regression: write_entry used Path.write_text, which opens the target with
    mode "w" and therefore truncates before writing — an interruption mid-write
    (crash / disk full) wiped every prior entry instead of just failing."""
    p = tmp_path / "log.md"
    original = "## 2026-08-01 — First\n\n### What was checked\n- important\n"
    p.write_text(original, encoding="utf-8")

    def boom(src, dst):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        selfdev.write_entry(p, "## 2026-08-11 — Second\n")

    assert p.read_text(encoding="utf-8") == original      # prior entries survive
    assert [f.name for f in tmp_path.iterdir()] == ["log.md"]  # temp cleaned up


def test_today_validates_format():
    assert selfdev.today("2026-08-11") == "2026-08-11"
    with pytest.raises(SystemExit):
        selfdev.today("2026/08/11")


def test_today_rejects_invalid_calendar_date():
    """today() must reject a non-existent calendar date (e.g. 2026-02-31), not
    just a malformed format — such an entry would be written yet stay invisible
    to latest_entry / _entry_age_days, making `check` report 'no dated entry'."""
    with pytest.raises(SystemExit):
        selfdev.today("2026-02-31")
    with pytest.raises(SystemExit):
        selfdev.today("2026-13-01")


# ── Branch coverage additions (2026-08-12) ───────────────────────────────────

def test_recent_blocks_non_positive_count():
    """recent_blocks with count<=0 returns no blocks (empty guard)."""
    assert selfdev.recent_blocks(SAMPLE, 0) == []
    assert selfdev.recent_blocks(SAMPLE, -1) == []


def test_today_defaults_to_today():
    """today(None) falls back to the current date (no arg path)."""
    assert selfdev.today(None) == dt.date.today().isoformat()


def test_print_missing_reports_entry_counts(capsys):
    """print_missing reports 'no entries' / 'only one entry' / counts correctly."""
    # review: 0 entries, experiment: 1 entry, decision: 2 entries, maintenance: 0
    selfdev.FILES["review"] = _ROOT / "tests" / "_fixture_missing_review.md"
    selfdev.FILES["experiment"] = _ROOT / "tests" / "_fixture_missing_experiment.md"
    selfdev.FILES["decision"] = _ROOT / "tests" / "_fixture_missing_decision.md"
    selfdev.FILES["maintenance"] = _ROOT / "tests" / "_fixture_missing_maintenance.md"
    try:
        Path(selfdev.FILES["review"]).write_text("", encoding="utf-8")
        Path(selfdev.FILES["experiment"]).write_text("## 2026-08-01 — Only one\n", encoding="utf-8")
        Path(selfdev.FILES["decision"]).write_text(SAMPLE, encoding="utf-8")  # 2 entries
        Path(selfdev.FILES["maintenance"]).write_text("", encoding="utf-8")

        assert selfdev.print_missing() == 0
        out = capsys.readouterr().out
        assert "review-log.md: no entries yet" in out
        assert "experiments.md: only one entry" in out
        assert "decisions.md: 2 entries" in out
        assert "maintenance.md: no entries yet" in out
    finally:
        for key in ("review", "experiment", "decision", "maintenance"):
            Path(selfdev.FILES[key]).unlink(missing_ok=True)


def test_port_status_reports_in_use():
    """_port_status reports IN USE when another socket holds the port."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", 0))  # ephemeral port
        s.listen(1)
        port = s.getsockname()[1]
        assert selfdev._port_status(port) == f"port {port}: IN USE"
    # After releasing the socket it should report free (may race, but generally true).
    status = selfdev._port_status(port)
    assert status in (f"port {port}: free", f"port {port}: IN USE")


# ── Final branch coverage (2026-08-16: 96% → ~100%) ─────────────────────────

def test_env_prereq_anthropic_installed(monkeypatch):
    """env_prereq_lines reports version when anthropic is importable."""
    import sys
    import types
    fake = types.ModuleType("anthropic")
    fake.__version__ = "0.99.0"
    monkeypatch.setitem(sys.modules, "anthropic", fake)
    lines = selfdev.env_prereq_lines()
    assert lines[0] == "anthropic: installed (0.99.0)"


def test_env_prereq_fastapi_missing(monkeypatch):
    """env_prereq_lines reports fastapi NOT installed when import fails."""
    import sys
    monkeypatch.setitem(sys.modules, "fastapi", None)  # forces ImportError on `import fastapi`
    lines = selfdev.env_prereq_lines()
    assert lines[1] == "fastapi: NOT installed"


def test_print_check_reports_syntax_error(monkeypatch, tmp_path, capsys):
    """check must surface a py_compile failure instead of crashing."""
    import py_compile
    _patch_files(monkeypatch, tmp_path)
    def boom(*args, **kwargs):
        exc = SyntaxError("syntax broke")
        raise py_compile.PyCompileError(SyntaxError, exc, None, "selfdev.py")
    monkeypatch.setattr(py_compile, "compile", boom)
    assert selfdev.print_check() == 0
    out = capsys.readouterr().out
    assert "selfdev.py: SYNTAX ERROR" in out


def test_print_status_shows_latest_entry(monkeypatch, tmp_path, capsys):
    """print_status prints the latest entry line when a log has entries."""
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "review.md").write_text(SAMPLE, encoding="utf-8")
    assert selfdev.print_status() == 0
    out = capsys.readouterr().out
    assert "latest: 2026-07-15 — Second entry" in out


def test_print_capsule_shows_latest_entry(monkeypatch, tmp_path, capsys):
    """print_capsule prints key_latest lines for logs that have entries."""
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "review.md").write_text(SAMPLE, encoding="utf-8")
    assert selfdev.main(["capsule"]) == 0
    out = capsys.readouterr().out
    assert "selfdev: review_latest=2026-07-15 — Second entry" in out


def test_main_unknown_command_exits():
    """main with an unrecognized subcommand exits with code 2 (argparse)."""
    import subprocess
    with pytest.raises(SystemExit) as exc:
        selfdev.main(["definitely-not-a-command"])
    assert exc.value.code == 2


def test_script_direct_run_smoke(tmp_path):
    """Running `python selfdev.py status` exits 0 (covers the __main__ guard)."""
    import subprocess
    res = subprocess.run(
        ["python3", str(_ROOT / "selfdev.py"), "status"],
        capture_output=True, text=True, timeout=30,
    )
    assert res.returncode == 0
    assert "Self-development project status" in res.stdout


# ── next_actions_from_plan robustness (2026-09-03) ───────────────────────────

def test_next_actions_robust_to_indentation_and_subheadings():
    """Plan with an indented heading, '### ' sub-sections and a bare '-' bullet
    must parse cleanly: sub-headings do not end capture, empty bullets are
    dropped, and leading whitespace is ignored."""
    plan = (
        "  ## Next actions  \n"
        "### Track A\n"
        "    - do the thing\n"
        "- \n"
        "### Track B — Local Agent Platform\n"
        "- ⏳ awaiting user confirmation\n"
        "## Other\n"
        "- not an action\n"
    )
    assert selfdev.next_actions_from_plan(plan) == [
        "do the thing",
        "⏳ awaiting user confirmation",
    ]


def test_next_actions_strips_checkbox_markers():
    """Task-list checkboxes ('- [ ]' / '- [x]') are stripped from item text, but
    a bracket citation like '- [ref] note' is left intact."""
    plan = (
        "## Next actions\n"
        "- [ ] open task\n"
        "- [x] done task\n"
        "- [ ]\n"
        "- [ref] citation stays\n"
        "## Other\n"
    )
    assert selfdev.next_actions_from_plan(plan) == [
        "open task",
        "done task",
        "[ref] citation stays",
    ]


def test_print_status_omits_entry_count_for_non_log_files(monkeypatch, tmp_path, capsys):
    """plan/README/context are static docs, not dated logs, so status must not
    report a misleading '0 entries' count for them."""
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "plan.md").write_text("# plan\n\nsome plan text\n", encoding="utf-8")
    assert selfdev.print_status() == 0
    out = capsys.readouterr().out
    assert "plan.md: present" in out
    assert "plan.md: present; 0 entries" not in out


def test_capsule_top_commands_include_check(monkeypatch, tmp_path, capsys):
    """The resume capsule's top_commands must include `check`, since it drives
    the recurring maintenance cadence (a standing Next action)."""
    _patch_files(monkeypatch, tmp_path)
    assert selfdev.main(["capsule"]) == 0
    out = capsys.readouterr().out
    assert "selfdev: top_commands=status, status --recent 2, missing, capsule, check" in out


def test_next_actions_h1_section_ends_capture():
    """An H1 top-level section after '## Next actions' must end capture, so a
    trailing '# ...' section cannot leak its bullets into next-actions (only
    H3+ sub-headings inside the block are skipped, not top-level H1/H2)."""
    plan = (
        "## Next actions\n"
        "- keep going\n"
        "\n"
        "# Archived\n"
        "- leaked bullet\n"
    )
    assert selfdev.next_actions_from_plan(plan) == ["keep going"]


def test_next_actions_empty_or_no_heading():
    """Empty text and text with no '## Next actions' heading both return []."""
    assert selfdev.next_actions_from_plan("") == []
    assert selfdev.next_actions_from_plan("# Only a doc\n\nno actions here\n") == []


# ── Empty-title / --recent validation (2026-09-11) ───────────────────────────

def test_require_text_rejects_empty_and_whitespace():
    """An empty or whitespace-only required value is rejected, not written."""
    with pytest.raises(SystemExit):
        selfdev.require_text("", "title")
    with pytest.raises(SystemExit):
        selfdev.require_text("   ", "title")


def test_require_text_trims_surrounding_whitespace():
    assert selfdev.require_text("  real title  ", "title") == "real title"


@pytest.mark.parametrize("formatter", [
    "format_review", "format_experiment", "format_decision", "format_maintenance",
])
def test_format_funcs_reject_empty_title(formatter):
    """Empty --title must not produce a header ENTRY_RE cannot parse.

    Regression: '## <date> — ' was counted as 0 entries / latest None, i.e. a
    ghost entry invisible to status/check/capsule."""
    args = _mk_args(date="2026-09-11", title="   ", checked=[], promising=[],
                    not_worth=[], decision="adopt", follow_up=[], hypothesis=[],
                    change_made=[], result=[], verdict="keep", lesson=[], why=[],
                    applies_to=[], notes=[], needs_attention=[], action=[])
    with pytest.raises(SystemExit):
        getattr(selfdev, formatter)(args)


def test_main_rejects_empty_title(monkeypatch, tmp_path):
    """CLI path also rejects --title '' rather than appending a ghost entry."""
    _patch_files(monkeypatch, tmp_path)
    with pytest.raises(SystemExit):
        selfdev.main(["review", "--title", "", "--decision", "adopt"])
    assert not (tmp_path / "review.md").exists()


def test_format_decision_rejects_empty_decision_value():
    """The `decision` command's --decision value is its substance; an empty or
    whitespace-only value must be rejected, not written as a blank
    '### Decision' section (argparse only enforces that the flag was passed)."""
    args = _mk_args(date="2026-09-12", title="A decision", decision="   ",
                    why=[], applies_to=[], notes=[])
    with pytest.raises(SystemExit):
        selfdev.format_decision(args)


def test_format_decision_trims_decision_value():
    args = _mk_args(date="2026-09-12", title="A decision", decision="  do it  ",
                    why=[], applies_to=[], notes=[])
    assert "### Decision\n- do it" in selfdev.format_decision(args)


def test_main_decision_rejects_empty_decision(monkeypatch, tmp_path):
    """CLI path also rejects --decision '' rather than writing a blank section."""
    _patch_files(monkeypatch, tmp_path)
    with pytest.raises(SystemExit):
        selfdev.main(["decision", "--title", "d", "--decision", ""])
    assert not (tmp_path / "decision.md").exists()


def test_build_parser_rejects_negative_recent():
    """status --recent must reject a negative count instead of silently falling
    back to the full status output."""
    parser = selfdev.build_parser()
    assert parser.parse_args(["status", "--recent", "2"]).recent == 2
    with pytest.raises(SystemExit):
        parser.parse_args(["status", "--recent", "-1"])
    with pytest.raises(SystemExit):
        parser.parse_args(["status", "--recent", "not-a-number"])


def test_main_status_recent_negative_exits(monkeypatch, tmp_path):
    _patch_files(monkeypatch, tmp_path)
    with pytest.raises(SystemExit):
        selfdev.main(["status", "--recent", "-2"])


# ── NOW.md handoff freshness in `check` (2026-09-11) ─────────────────────────

def test_now_updated_date_parses_and_validates():
    """Parse the `Updated:` field; absent/empty/invalid dates yield None."""
    assert selfdev.now_updated_date("Updated: 2026-09-11\n") == dt.date(2026, 9, 11)
    assert selfdev.now_updated_date("Updated:   2026-09-11  \n") == dt.date(2026, 9, 11)
    assert selfdev.now_updated_date("") is None
    assert selfdev.now_updated_date("# NOW\n\nno updated field\n") is None
    # A non-existent calendar date must not parse (mirrors the ghost-date guard).
    assert selfdev.now_updated_date("Updated: 2026-02-31\n") is None


def test_print_check_reports_now_stale(monkeypatch, tmp_path, capsys):
    """A long-stale NOW.md `Updated:` is flagged so the next session rebuilds it."""
    _patch_files(monkeypatch, tmp_path)
    old = (dt.date.today() - dt.timedelta(days=45)).isoformat()
    (tmp_path / "now.md").write_text(f"# NOW\n\nUpdated: {old}\n", encoding="utf-8")
    assert selfdev.print_check() == 0
    out = capsys.readouterr().out
    assert "now.md: STALE" in out
    assert "rebuild it per CLAUDE.md" in out


def test_print_check_reports_now_ok(monkeypatch, tmp_path, capsys):
    """A recently updated NOW.md reports its age as ok, next to log freshness."""
    _patch_files(monkeypatch, tmp_path)
    recent = (dt.date.today() - dt.timedelta(days=2)).isoformat()
    (tmp_path / "now.md").write_text(f"# NOW\n\nUpdated: {recent}\n", encoding="utf-8")
    assert selfdev.print_check() == 0
    out = capsys.readouterr().out
    assert "now.md: ok — updated 2d ago" in out


def test_print_check_reports_missing_now_updated(monkeypatch, tmp_path, capsys):
    """Without an `Updated:` field, check tells the user to add one (actionable)."""
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "now.md").write_text("# NOW\n\nno date here\n", encoding="utf-8")
    assert selfdev.print_check() == 0
    out = capsys.readouterr().out
    assert "now.md: no `Updated:` date" in out


# ── NOW.md handoff freshness in `status` (2026-09-12) ────────────────────────

def test_now_handoff_status_wording():
    """The shared helper words ok / STALE / missing-date consistently."""
    recent = (dt.date.today() - dt.timedelta(days=3)).isoformat()
    assert selfdev.now_handoff_status(f"Updated: {recent}\n") == "ok — updated 3d ago"
    old = (dt.date.today() - dt.timedelta(days=40)).isoformat()
    assert selfdev.now_handoff_status(f"Updated: {old}\n").startswith("STALE — updated 40d ago")
    assert selfdev.now_handoff_status("") == (
        "no `Updated:` date — add/refresh one so freshness is checkable"
    )


def test_print_status_reports_now_freshness(monkeypatch, tmp_path, capsys):
    """`status` (the primary command) must surface NOW.md freshness too, so a
    session that never runs `check` still sees the handoff state."""
    _patch_files(monkeypatch, tmp_path)
    recent = (dt.date.today() - dt.timedelta(days=1)).isoformat()
    (tmp_path / "now.md").write_text(f"# NOW\n\nUpdated: {recent}\n", encoding="utf-8")
    assert selfdev.print_status() == 0
    out = capsys.readouterr().out
    assert "- NOW.md: present; ok — updated 1d ago" in out


def test_print_status_flags_stale_now(monkeypatch, tmp_path, capsys):
    """A stale NOW.md is called out in `status`, not only in `check`."""
    _patch_files(monkeypatch, tmp_path)
    old = (dt.date.today() - dt.timedelta(days=45)).isoformat()
    (tmp_path / "now.md").write_text(f"# NOW\n\nUpdated: {old}\n", encoding="utf-8")
    assert selfdev.print_status() == 0
    out = capsys.readouterr().out
    assert "- NOW.md: present; STALE — updated 45d ago (rebuild it per CLAUDE.md)" in out


def test_print_status_reports_missing_now(monkeypatch, tmp_path, capsys):
    """A missing NOW.md is reported as `missing` with an actionable hint."""
    _patch_files(monkeypatch, tmp_path)
    assert selfdev.print_status() == 0
    out = capsys.readouterr().out
    assert "- NOW.md: missing; no `Updated:` date" in out


# ── NOW.md future `Updated:` guard (2026-09-13) ──────────────────────────────

def test_now_handoff_status_flags_future_date():
    """A future `Updated:` date must be flagged, not clamped to 'ok — 0d ago'.

    Clamping (as `_entry_age_days` does for pre-written log entries) would report
    a broken handoff as fresh forever; NOW.md is a handoff, so a future date is
    always wrong and must be surfaced."""
    future = (dt.date.today() + dt.timedelta(days=5)).isoformat()
    status = selfdev.now_handoff_status(f"Updated: {future}\n")
    assert status.startswith(f"FUTURE — Updated {future} is ahead of today")
    assert "fix the date" in status
    # A today-dated handoff stays ok (boundary: age 0 is not future).
    today = dt.date.today().isoformat()
    assert selfdev.now_handoff_status(f"Updated: {today}\n") == "ok — updated 0d ago"


def test_print_status_flags_future_now(monkeypatch, tmp_path, capsys):
    """`status` surfaces a future-dated NOW.md instead of calling it ok."""
    _patch_files(monkeypatch, tmp_path)
    future = (dt.date.today() + dt.timedelta(days=3)).isoformat()
    (tmp_path / "now.md").write_text(f"# NOW\n\nUpdated: {future}\n", encoding="utf-8")
    assert selfdev.print_status() == 0
    out = capsys.readouterr().out
    assert f"- NOW.md: present; FUTURE — Updated {future} is ahead of today" in out
    assert "ok — updated" not in out


def test_print_check_flags_future_now(monkeypatch, tmp_path, capsys):
    """`check` flags a future-dated NOW.md rather than reporting it fresh."""
    _patch_files(monkeypatch, tmp_path)
    future = (dt.date.today() + dt.timedelta(days=3)).isoformat()
    (tmp_path / "now.md").write_text(f"# NOW\n\nUpdated: {future}\n", encoding="utf-8")
    assert selfdev.print_check() == 0
    out = capsys.readouterr().out
    assert f"now.md: FUTURE — Updated {future} is ahead of today" in out


# ── NOW.md `Next:` content in the resume capsule (2026-09-15) ────────────────

def test_next_items_from_now_parses_numbered_and_bulleted():
    """`Next:` items lose their numbering / "- " marker, a blank line inside the
    block does not end capture, a bare "-" is dropped, and the following
    top-level field (Blockers:) does not leak in."""
    now = (
        "# NOW\n\nNext:\n"
        "  1. do the first thing\n"
        "\n"
        "  2. do the second thing\n"
        "  - a bulleted extra\n"
        "  -\n"
        "  - a third thing\n"
        "Blockers:\n"
        "- Track B needs user confirmation\n"
    )
    assert selfdev.next_items_from_now(now) == [
        "do the first thing",
        "do the second thing",
        "a bulleted extra",
        "a third thing",
    ]


def test_next_items_from_now_absent_or_empty():
    """No `Next:` field, empty text, or a field with no items all yield []."""
    assert selfdev.next_items_from_now("") == []
    assert selfdev.next_items_from_now("# NOW\n\nBlockers:\n- x\n") == []
    assert selfdev.next_items_from_now("Next:\nBlockers:\n- nothing here\n") == []


def test_next_items_from_now_inline_value():
    """A one-line `Next: <text>` field is captured as a single item."""
    assert selfdev.next_items_from_now("Next: ship it\n") == ["ship it"]


def test_next_items_from_now_plain_indented_line():
    """A hand-written item with no marker is kept, not silently dropped."""
    assert selfdev.next_items_from_now("Next:\n  plain item\n") == ["plain item"]


def test_main_capsule_reports_now_next(monkeypatch, tmp_path, capsys):
    """The resume capsule surfaces NOW.md's `Next` — CLAUDE.md's default next
    step — not only plan.md's action list."""
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "now.md").write_text(
        "# NOW\n\nNext:\n"
        "  1. unblock Track B\n"
        "  2. run the spike\n"
        "  3. re-check maintenance\n"
        "\nBlockers:\n- user confirmation\n",
        encoding="utf-8")
    assert selfdev.main(["capsule"]) == 0
    out = capsys.readouterr().out
    assert "selfdev: now_next=unblock Track B" in out
    assert "selfdev: now_next_more=2" in out
    assert "- user confirmation" not in out  # Blockers section must not leak


def test_main_capsule_omits_now_next_when_absent(monkeypatch, tmp_path, capsys):
    """Without a `Next:` field the capsule stays as before (no empty key)."""
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "now.md").write_text("# NOW\n\nUpdated: 2026-09-15\n", encoding="utf-8")
    assert selfdev.main(["capsule"]) == 0
    out = capsys.readouterr().out
    assert "now_next" not in out


def test_main_capsule_omits_now_next_more_for_single_item(monkeypatch, tmp_path, capsys):
    """A single Next item is reported without a remainder count."""
    _patch_files(monkeypatch, tmp_path)
    (tmp_path / "now.md").write_text(
        "# NOW\n\nNext:\n  1. only one thing\n", encoding="utf-8")
    assert selfdev.main(["capsule"]) == 0
    out = capsys.readouterr().out
    assert "selfdev: now_next=only one thing" in out
    assert "now_next_more" not in out
