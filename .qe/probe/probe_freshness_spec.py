"""Fourth-pass QE: the freshness checker against docs/FRESHNESS.md.

The specification is the oracle. Every case here builds a real repository and makes a
real commit, as `test_freshness.py` does, because the checker's whole subject is what git
says about two revisions of a file.
"""

import subprocess

from claims_ledger import freshness, resolve, validate
from claims_ledger.schema import exit_code, git, open_ledger

NOTE = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.
"""


def _rev(project, *args):
    out = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def build(project, grounds, pin=None):
    """An entry whose Grounds are `grounds` (pointer lines, `{pin}` formatted with the
    pin), on a repository whose artifacts were committed first. Returns (path, pin)."""
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the artifacts, before any claim rests on them", "--allow-empty")
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


def outcomes(project, write=False):
    return [
        (r.outcome, r.part, r.message)
        for r in freshness.run(open_ledger(root=project.root), write=write)
    ]


def append(path, block):
    text = path.read_text(encoding="utf-8")
    head, marker, tail = text.partition("\n## References")
    path.write_text(head.rstrip("\n") + "\n\n" + block + marker + tail, encoding="utf-8")


def contested(pointer_line, note="propagated from a moved ground"):
    return (
        "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
        f"  evidence: {pointer_line}\n"
        f"  note: {note}\n"
    )


# --- exploration ----------------------------------------------------------------------


def test_explore_glob(project):
    (project.root / "docs" / "note[1].md").write_text(NOTE, encoding="utf-8")
    (project.root / "docs" / "note1.md").write_text(NOTE, encoding="utf-8")
    build(project, ["experiment: docs/note[1].md @{pin}"])
    (project.root / "docs" / "note1.md").write_text(NOTE.replace("0.04", "0.09"), encoding="utf-8")
    print("EDITED THE DECOY:", outcomes(project))
    print("RESOLVE:", [r.message for r in resolve.run(open_ledger(root=project.root))])
    print("VALIDATE:", [r.message for r in validate.run(open_ledger(root=project.root))])


def test_explore_pathspec_magic(project):
    (project.root / "docs" / ":note.md").write_text(NOTE, encoding="utf-8")
    build(project, ["experiment: docs/:note.md @{pin}"])
    pin = _rev(project, "--short", "HEAD~1")
    print("verify:", repr(git(project.root, "rev-parse", "--verify", f"{pin}:docs/:note.md")))
    (project.root / "docs" / ":note.md").write_text(NOTE.replace("0.04", "0.09"), encoding="utf-8")
    print("DIFF:", repr(git(project.root, "diff", "--name-only", pin, "--", "docs/:note.md")))
    print("EDITED:", outcomes(project))
    print("RESOLVE:", [r.message for r in resolve.run(open_ledger(root=project.root))])


def test_explore_uppercase(project):
    (project.root / "docs" / "other.md").write_text(NOTE, encoding="utf-8")
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts")
    up = _rev(project, "HEAD").upper()
    build(project, ["experiment: docs/other.md @{pin}"], pin=up)
    print("RESOLVE:", [r.message for r in resolve.run(open_ledger(root=project.root))])
    print("VALIDATE:", [r.message for r in validate.run(open_ledger(root=project.root))])
    (project.root / "docs" / "other.md").unlink()
    print("DELETED:", outcomes(project))
    print("CLI EXIT:", project.cl("freshness"))


def test_explore_symlink(project):
    (project.root / "docs" / "target.md").write_text(NOTE, encoding="utf-8")
    (project.root / "docs" / "link.md").symlink_to("target.md")
    build(project, ["experiment: docs/link.md @{pin}"])
    (project.root / "docs" / "target.md").unlink()
    print("DANGLING:", outcomes(project))
    print("GIT STATUS:", repr(git(project.root, "status", "--porcelain")))
    print("RESOLVE:", [r.message for r in resolve.run(open_ledger(root=project.root))])


def test_explore_unreadable(project):
    (project.root / "docs" / "sub").mkdir()
    (project.root / "docs" / "sub" / "art.md").write_text(NOTE, encoding="utf-8")
    build(project, ["experiment: docs/sub/art.md @{pin}"])
    (project.root / "docs" / "sub").chmod(0o000)
    try:
        print("UNREADABLE:", outcomes(project))
        print("GIT STATUS:", repr(git(project.root, "status", "--porcelain")))
    finally:
        (project.root / "docs" / "sub").chmod(0o755)


def test_explore_section_key(project):
    path, pin = build(project, ['lab: docs/note-001.md § "Observation" @{pin}'])
    (project.root / "docs" / "note-001.md").unlink()
    print("BEFORE:", outcomes(project))
    append(path, contested(f'lab: docs/note-001.md § "Elsewhere" @{pin}'))
    print("AFTER:", outcomes(project))
    print("VALIDATE:", [r.message for r in validate.run(open_ledger(root=project.root))])


def test_explore_terminal_orphan(project):
    path, pin = build(project, ['lab: docs/note-001.md § "Observation" @{pin}'])
    append(
        path,
        contested(f'lab: docs/note-001.md § "Observation" @{pin}')
        + "\n- 2026-11-21T09:00:00-08:00 · refuted · grade: measured · author: main\n"
        f'  evidence: lab: docs/note-001.md § "Observation" @{pin}\n'
        "  note: the sweep did not replicate\n",
    )
    print("FALLEN, GROUND NOT DRIFTED:", outcomes(project))
    print("VALIDATE:", [r.message for r in validate.run(open_ledger(root=project.root))])


def test_explore_unstable_pin_orphan(project):
    path, pin = build(project, ['lab: docs/note-001.md § "Observation" @{pin}'])
    project.git("branch", "beef")
    text = path.read_text(encoding="utf-8").replace(f"@{pin}", "@beef")
    path.write_text(text, encoding="utf-8")
    append(path, contested('lab: docs/note-001.md § "Observation" @beef'))
    print("UNSTABLE + VERDICT:", outcomes(project))


def test_explore_write_exit_code(project):
    path, _ = build(project, ['lab: docs/note-001.md § "Observation" @{pin}'])
    before = path.read_text(encoding="utf-8")
    (project.root / "docs" / "note-001.md").write_text(
        NOTE.replace("0.04", "0.09"), encoding="utf-8"
    )
    reports = freshness.run(open_ledger(root=project.root), write=True)
    print("REPORTS:", [(r.outcome, r.message) for r in reports])
    print("EXIT:", exit_code(reports), "CLI EXIT:", project.cl("freshness", "--write"))
    after = path.read_text(encoding="utf-8")
    print("MODIFIED:", before != after, "COUNT:", after.count("author: propagation"))
    print("SECOND RUN:", outcomes(project, write=True))
