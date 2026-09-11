"""What a propagated record and a reading mean to each other when both are stated by value.

The fix-review gate on the grounds-by-value branch (qe ticket c4e62619f4d5476f) measured
a flag no legal edit could clear: a by-value drift recorded, committed and reverted, with
the only reading a person could write refused as a restatement. These hold the repair —
a record is moved past by any later reading of the ground, and a reading may name the
ground's own digest — and the mutants that survived the gate's sweep beside it. Every
case builds a real repository.
"""

import os
import subprocess
from datetime import datetime

from test_git_degradation import _shim_git_that_cannot

from claims_ledger import freshness, resolve, validate
from claims_ledger.schema import open_ledger

NOTE = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.
"""

TWO_SECTIONS = (
    NOTE
    + """
## Method

Ten sweeps at each fraction, averaged.
"""
)


def reports(project, checker=freshness):
    return [(r.outcome, r.part, r.message) for r in checker.run(open_ledger(root=project.root))]


def note(project, text):
    (project.root / "docs" / "note-001.md").write_text(text, encoding="utf-8")


def commit_all(project, message):
    project.git("add", "-A")
    project.git("commit", "-qm", message)


def head(project):
    out = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def ground(project, section="Observation"):
    digest = project.digest("docs/note-001.md", section)
    return f'- lab: docs/note-001.md § "{section}" ={digest}'


def entry_with(project, grounds=None):
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    grounds = grounds or [ground(project)]
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working', "\n".join(grounds)
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    return path


def now():
    """Stamped when written, as the tool stamps the records these sit beside: a verdict's
    timestamp may not precede the one above it."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def append(project, block):
    path = next(project.entries.glob("A0001-*.md"))
    text = path.read_text(encoding="utf-8")
    head_, marker, tail = text.partition("\n## References")
    path.write_text(head_.rstrip("\n") + "\n\n" + block + marker + tail, encoding="utf-8")


def reading(digest, section="Observation", note_="read again"):
    return (
        f"- {now()} · corroborated · grade: measured · author: main\n"
        f'  evidence: lab: docs/note-001.md § "{section}" ={digest}\n'
        f"  note: {note_}\n"
    )


def propagated(raw, artifact, note_="propagated from a moved ground"):
    """A record written by hand, as a forger would write it: the tool only ever records the
    digest it just read, so the artifact is the one thing a fixture has to choose itself."""
    return (
        f"- {now()} · contested · grade: measured · author: propagation\n"
        f"  evidence: {raw}\n"
        f"  artifact: {artifact}\n"
        f"  note: {note_}\n"
    )


def record(project):
    """`freshness --write`, as the hook would run it: the drift in front of the run, recorded."""
    assert project.cl("freshness", "--write") == 1


def test_a_drift_recorded_and_reverted_is_cleared_by_a_reading_of_the_grounds_own_digest(
    project,
):
    """QE18-1. Before the fix the flag at step 3 was permanent: the only reading that
    could move the record past was `=D0`, and validate refused it as a restatement."""
    project.git("init", "-q")
    entry_with(project)
    d0 = project.digest("docs/note-001.md", "Observation")
    commit_all(project, "claim and note")
    note(project, NOTE.replace("0.04", "0.09"))
    record(project)
    commit_all(project, "drift recorded")
    note(project, NOTE)
    commit_all(project, "reverted to the anchor's text")
    ((outcome, part, message),) = reports(project)
    assert (outcome, part) == ("flag", "Verdicts")
    assert "nothing can confirm it" in message
    append(project, reading(d0, note_="read again after the revert: as the ground states it"))
    assert [r for r in reports(project, validate) if r[0] == "fail"] == []
    assert reports(project) == []


def test_a_reading_by_reference_may_still_not_restate_a_ground(project):
    """The by-value admission is narrow: a corroboration `@<pin>` naming the ground's own
    pointer says nothing a reading could, and is still refused."""
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the note")
    pin = head(project)
    entry_with(project, [f'- lab: docs/note-001.md § "Observation" @{pin}'])
    append(
        project,
        f"- {now()} · corroborated · grade: measured · author: main\n"
        f'  evidence: lab: docs/note-001.md § "Observation" @{pin}\n'
        "  note: restated\n",
    )
    fails = [r for r in reports(project, validate) if r[0] == "fail"]
    assert len(fails) == 1 and "does not already cite" in fails[0][2]


def test_a_record_after_the_latest_reading_flags_and_a_further_reading_moves_it_past(project):
    """QE18-4, the gate's P1: with the moved-past rule keyed on the pointer's text, a
    second reading of the same digest changed nothing, and deleting the line that kept
    the current reading out of `moved_past` was caught by no test."""
    project.git("init", "-q")
    entry_with(project)
    commit_all(project, "claim and note")
    note(project, NOTE.replace("0.04", "0.09"))
    record(project)
    commit_all(project, "first drift recorded")
    d1 = project.digest("docs/note-001.md", "Observation")
    append(project, reading(d1))
    commit_all(project, "reading R1")
    assert reports(project) == []
    note(project, NOTE.replace("0.04", "0.12"))
    record(project)
    commit_all(project, "second drift recorded, against R1")
    note(project, NOTE.replace("0.04", "0.09"))
    commit_all(project, "reverted to what R1 read")
    ((outcome, part, message),) = reports(project)
    assert (outcome, part) == ("flag", "Verdicts")
    assert "verdict 3" in message and "nothing can confirm it" in message
    append(project, reading(d1, note_="read once more"))
    assert reports(project) == []
    assert [r for r in reports(project, validate) if r[0] == "fail"] == []


def test_a_record_against_the_ground_does_not_discharge_a_drift_from_a_later_reading(project):
    """Mutant L5: `acknowledgements` matched a record to a pointer without its digest,
    so a record against the ground discharged a drift compared from a reading."""
    project.git("init", "-q")
    entry_with(project)
    commit_all(project, "claim and note")
    note(project, NOTE.replace("0.04", "0.12"))
    record(project)  # records 0.12, against the ground
    commit_all(project, "drift recorded")
    note(project, NOTE.replace("0.04", "0.09"))
    d1 = project.digest("docs/note-001.md", "Observation")
    note(project, NOTE.replace("0.04", "0.12"))
    append(project, reading(d1, note_="a reading of 0.09, never in the tree"))
    found = reports(project)
    assert any(o == "flag" and p == "Grounds 1" and "has moved" in m for o, p, m in found), found


def test_a_by_value_reading_of_one_section_is_not_a_reading_of_another(project):
    """Mutant L6: `readings` matched a by-value corroboration to a ground without its
    section, so a reading of Method became the baseline Observation was compared from."""
    project.git("init", "-q")
    note(project, TWO_SECTIONS)
    entry_with(project, [ground(project), ground(project, "Method")])
    commit_all(project, "claim and note")
    note(project, TWO_SECTIONS.replace("Ten sweeps", "Twelve sweeps"))
    append(project, reading(project.digest("docs/note-001.md", "Method"), section="Method"))
    assert reports(project) == []


def test_an_orphan_is_not_accused_on_a_ground_that_could_not_be_read(project):
    """Mutant L10, on a ground stated by value. The skip has to hold where `anchor_digest`
    still answers — by value it asks git nothing — or the refuted rule runs on a comparison
    that was never made. The by-reference case below cannot see this: there the same git
    that could not hand over the artifact cannot compute the anchor either, so the refuted
    rule finds nothing to fire on and the mutant survives the assertion."""
    project.git("init", "-q")
    g = ground(project)
    entry_with(project, [g])
    commit_all(project, "claim and note")
    append(project, propagated(g.removeprefix("- "), project.digest("docs/note-001.md", "Observation")))
    commit_all(project, "a record naming the anchor's own digest")
    (project.root / "docs" / "note-001.md").chmod(0o000)
    try:
        got = reports(project)
    finally:
        (project.root / "docs" / "note-001.md").chmod(0o644)
    # One report, and it is the unread ground. With the skip gone the refuted rule runs
    # anyway and accuses the record of stating no drift, on a section nothing compared.
    assert [(o, p) for o, p, _ in got] == [("fail", "Grounds 1")], got
    assert "records the artifact as the pin itself has it" not in "".join(m for _, _, m in got)


def test_an_orphan_is_not_accused_on_a_ground_git_could_not_compare(project, tmp_path, monkeypatch):
    """The same skip, reached through a git that cannot hand over the pinned blob. This one
    does not kill mutant L10 on its own — see the by-value case above — and is kept for the
    `was not checked` path it does cover."""
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the note")
    entry_with(project, [f'- lab: docs/note-001.md § "Observation" @{head(project)}'])
    commit_all(project, "claim")
    note(project, NOTE.replace("0.04", "0.09"))
    record(project)
    commit_all(project, "drift recorded")
    note(project, NOTE)
    commit_all(project, "reverted")
    before = reports(project)
    assert [o for o, _, _ in before] == ["flag"], before
    shim = _shim_git_that_cannot(tmp_path, "show")
    monkeypatch.setenv("PATH", f"{shim}{os.pathsep}{os.environ['PATH']}")
    after = reports(project)
    assert [o for o, _, _ in after] == ["fail"], after
    assert "was not checked" in after[0][2]


def test_a_founding_text_held_only_on_another_ref_still_resolves(project):
    """Mutant R2: `--all` dropped from the history search. After an amend the founding
    text is on no branch HEAD reaches, but a ref that still names the old commit holds it."""
    project.git("init", "-q")
    entry_with(project)
    commit_all(project, "claim and note")
    project.git("branch", "keep")
    note(project, NOTE.replace("0.04", "0.09"))
    project.git("add", "-A")
    project.git("commit", "-q", "--amend", "--no-edit")
    assert reports(project, resolve) == []
    project.git("branch", "-D", "keep")
    got = reports(project, resolve)
    assert [o for o, _, _ in got] == ["flag"], got


def test_under_cached_a_by_value_anchor_is_held_to_the_index(project):
    """QE18-2, the gate's P2: index holds one text and the working tree another; the
    anchor digests to the tree's. The hook reads the index, and a read of the tree there
    let the entry land with an anchor no version of the path would hold."""
    project.git("init", "-q")
    note(project, NOTE.replace("0.04", "0.09"))
    project.git("add", "-A")
    note(project, NOTE)
    entry_with(project)
    project.git("add", "ledger")
    assert reports(project, resolve) == []
    run = resolve.run(open_ledger(root=project.root), cached=True)
    ((outcome, part, message),) = [(r.outcome, r.part, r.message) for r in run]
    assert (outcome, part) == ("fail", "Grounds 1")
    assert "names text the index does not hold" in message


def test_sha_write_fills_a_pointer_line_and_not_prose_that_ends_the_same_way(project):
    """QE18-3, the gate's P4b: a Warrant sentence ending in the pending pointer's text sat
    in the frozen region of a committed entry, and the fill rewrote it at exit 0."""
    project.git("init", "-q")
    path = entry_with(project)
    text = path.read_text(encoding="utf-8")
    prose = 'Re-read later as lab: docs/note-001.md § "Observation" =?'
    path.write_text(text.replace("## Warrant\n\n", f"## Warrant\n\n{prose}\n", 1), encoding="utf-8")
    commit_all(project, "claim, with a pending-looking sentence in prose")
    frozen = path.read_text(encoding="utf-8").partition("<!-- APPEND")[0]
    append(project, reading("?"))
    assert project.cl("sha", "--write", str(path)) == 0
    after = path.read_text(encoding="utf-8")
    assert after.partition("<!-- APPEND")[0] == frozen
    assert prose in after
    assert f"  evidence: {ground(project)[2:]}" in after
    assert [r for r in reports(project, validate) if r[0] == "fail"] == []
