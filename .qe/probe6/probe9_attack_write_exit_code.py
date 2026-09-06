"""QE6 — Part 2f: attack HIGH-30's exit-code fix across combinations: moved + withdrawn
together, and confirm a --write run that appends NOTHING still exits 0 (correctly)."""

import subprocess

from claims_ledger import freshness
from claims_ledger.schema import open_ledger, exit_code


def _rev(project, *args):
    out = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", *args],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def build(project, grounds, pin=None):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts", "--allow-empty")
    pin = pin or _rev(project, "--short", "HEAD")
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    lines = "\n".join("- " + g.format(pin=pin) for g in grounds)
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working', lines
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    return path, pin


def test_moved_and_withdrawn_together(project):
    note2 = project.root / "docs" / "note-002.md"
    note2.write_text("# note 002\n\nsome content\n", encoding="utf-8")
    path, pin = build(project, [
        "experiment: docs/note-001.md @{pin}",
        "experiment: docs/note-002.md @{pin}",
    ])
    (project.root / "docs" / "note-001.md").write_text("edited\n", encoding="utf-8")
    note2.unlink()
    reports = freshness.run(open_ledger(root=project.root), write=True)
    code = exit_code(reports)
    print("MOVED+WITHDRAWN+write:", [(r.outcome, r.message) for r in reports], "exit:", code)
    assert code != 0
    assert all(r.outcome == "fail" for r in reports if "appended" in r.message or "Grounds" in r.part)


def test_write_with_nothing_to_append_exits_zero(project):
    path, pin = build(project, ["experiment: docs/note-001.md @{pin}"])
    reports = freshness.run(open_ledger(root=project.root), write=True)
    code = exit_code(reports)
    print("WRITE with nothing to append:", reports, "exit:", code)
    assert code == 0
    assert reports == []


def test_second_write_after_first_appends_nothing(project):
    art = project.root / "docs" / "note-001.md"
    path, pin = build(project, ["experiment: docs/note-001.md @{pin}"])
    art.write_text("edited\n", encoding="utf-8")
    r1 = freshness.run(open_ledger(root=project.root), write=True)
    print("FIRST write:", [(r.outcome, r.message) for r in r1], "exit:", exit_code(r1))
    assert exit_code(r1) != 0
    r2 = freshness.run(open_ledger(root=project.root), write=True)
    print("SECOND write (should append nothing new):", [(r.outcome, r.message) for r in r2],
          "exit:", exit_code(r2))
    # The ground is now acknowledged, so the second write appends nothing -- but is it
    # still reported as 'moved'? has_acknowledged suppresses the flag, so nothing should
    # be pending and exit should be 0 on the second run.
    assert exit_code(r2) == 0
