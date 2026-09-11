"""The discharge protocol: what a verdict over a pinned ground must record, and what
silences a drift.

`docs/FRESHNESS.md` specifies it. A propagated verdict names the artifact it was written
against; a hand-written one may not; the orphan rule refuses a ground no verdict caused;
and a drift is silenced only by a verdict that actually describes it. The `artifact:`
line is the field the whole rule rests on, and the tests below are the only thing holding
it to a shape.

The two cases at the end were strict xfails while `docs/FRESHNESS.md` stated them as
residuals of a rule that asked history; the rule asks none now, and they pass.

Every case builds a real repository and makes real commits. Nothing patches git, the
filesystem or the package — a git that cannot answer is produced by putting a shim on
PATH, because `freshness.py` does `from .schema import git` and patching the module
attribute would not reach it.
"""

from __future__ import annotations

import os
import subprocess

from test_freshness import pinned  # noqa: F401  — the fixture, reused as-is
from test_freshness_spec import build

from claims_ledger import freshness, validate
from claims_ledger.schema import NULL_OBJECT_ID, open_ledger

NOTE = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.
"""


def propagated(pin, artifact=None):
    """A propagated verdict against the pinned ground, as `freshness --write` writes one."""
    line = f"  artifact: {artifact}\n" if artifact is not None else ""
    return (
        "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
        f'  evidence: lab: docs/note-001.md § "Observation" @{pin}\n'
        f"{line}"
        "  note: propagated from a moved ground\n"
    )


def failures(pinned, checker=validate):  # noqa: F811
    return [
        (r.part, r.message)
        for r in checker.run(open_ledger(root=pinned.root))
        if r.outcome == "fail"
    ]


FENCED_NOTE = (
    "# note 001\n\n"
    "## Observation\n\n"
    "At a stale fraction of 0.1 the measured error was 0.04.\n\n"
    "```python\n"
    "# the sweep, as run\n"
    "sweep(stale=0.1)\n"
    "```\n\n"
    "The error does not grow with degree.\n"
)


def outcomes(root):
    return [(r.outcome, r.part, r.message) for r in freshness.run(open_ledger(root=root))]


def shim_git(tmp_path, failing_subcommand):
    """A `git` on PATH that fails one subcommand and delegates everything else to the real one. A
    repository this git cannot fully answer is an ordinary condition — a corrupted object, a
    clean filter that fails, a history too large for the timeout — and the package's own rule
    is that a git which cannot answer is not a git saying no.
    """
    d = tmp_path / "shim-bin"
    d.mkdir(exist_ok=True)
    real = subprocess.run(["which", "git"], capture_output=True, text=True, check=True)
    (d / "git").write_text(
        "#!/bin/sh\n"
        f'for a in "$@"; do [ "$a" = "{failing_subcommand}" ] && exit 128; done\n'
        f'exec {real.stdout.strip()} "$@"\n',
        encoding="utf-8",
    )
    (d / "git").chmod(0o755)
    return d


FORGERY = (
    "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
    '  evidence: lab: docs/note-001.md § "Observation" @{pin}\n'
    "  artifact: {artifact}\n"
    "  note: propagated from a moved ground\n"
)


def test_a_propagated_verdict_over_a_pinned_ground_must_record_an_artifact(pinned):  # noqa: F811
    """The discharge rests entirely on what the verdict states it was caused by. A verdict
    that states nothing is one nothing can ever check, and it used to be the shape every
    verdict this package had ever written before the field existed."""
    pinned.append(propagated(pinned.pin))
    assert any("no artifact: line" in m for _, m in failures(pinned))


def test_an_artifact_that_is_not_an_object_id_is_refused(pinned):  # noqa: F811
    """Four shapes, one rule. `ABSENT` in the wrong case is here because the value is
    compared as bytes everywhere it is read, so a checker that accepted it would be
    accepting a word that means nothing to the code that acts on it."""
    for value in ("not-a-hash", "ABSENT", "abc", "0" * 39):
        pinned.append(propagated(pinned.pin, value))
        assert any(f"artifact `{value}`" in m for _, m in failures(pinned)), value
        _drop_last_verdict(pinned)


def test_the_null_object_id_is_refused(pinned):  # noqa: F811
    """Forty hex characters that name nothing. It passes the shape, and `blobs_since()`
    drops it from what the path has held, so it is a value nothing could ever confirm —
    which is exactly what made it a way to write a discharge that no rule could reach."""
    pinned.append(propagated(pinned.pin, NULL_OBJECT_ID))
    assert any("null object id" in m for _, m in failures(pinned))


def test_an_artifact_on_a_hand_written_verdict_is_refused(pinned):  # noqa: F811
    """The other direction, and the one that lets a person fabricate machine provenance:
    `artifact:` is what `freshness --write` records, so on a `corroborated` verdict signed
    by a person it is provenance nothing machine produced.

    The message states the shape rather than the intent (QE8-88 of the second round): the
    rule cannot tell a person fabricating provenance from a verdict the machinery really
    wrote under a `propagation-author` the configuration has since been changed away from,
    and it said "claims a check that did not run" about every verdict in the ledger after
    that one-line edit."""
    pinned.append(
        "- 2026-11-20T09:00:00-08:00 · corroborated · grade: measured · author: main\n"
        "  evidence: experiment: docs/note-001.md @working\n"
        f"  artifact: {pinned.p.blob('docs/note-001.md')}\n"
        "  note: read again and it still says so\n"
    )
    assert any("this verdict is not that shape" in m for _, m in failures(pinned))


def test_a_second_artifact_line_is_malformed(pinned):  # noqa: F811
    """The last one silently won, so a verdict could carry the value a reader sees and the
    value the checkers read, and they did not have to be the same value."""
    real = pinned.p.blob("docs/note-001.md")
    pinned.append(
        "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
        f'  evidence: lab: docs/note-001.md § "Observation" @{pinned.pin}\n'
        f"  artifact: {real}\n"
        f"  artifact: {NULL_OBJECT_ID}\n"
        "  note: propagated from a moved ground\n"
    )
    assert any("a second `artifact:` line" in m for _, m in failures(pinned))


def _drop_last_verdict(pinned):  # noqa: F811
    """Remove the block this test just appended, so the next value is asked on its own.

    The entry is uncommitted here, so this is an edit a person could make; `check_history`
    holds the append-only rule over what git has, and git has none of these.
    """
    path = pinned.entry_path()
    text = path.read_text(encoding="utf-8")
    head, marker, tail = text.partition("\n## References")
    blocks = [b for b in head.split("\n\n- ")]
    path.write_text("\n\n- ".join(blocks[:-1]) + "\n" + marker + tail, encoding="utf-8")


def test_a_well_formed_artifact_is_accepted(pinned):  # noqa: F811
    """The control for all five above. Neither of the two legal values is a failure, and a
    rule that refused them would refuse every verdict the machinery writes."""
    pinned.note(NOTE.replace("0.04", "0.09"))
    pinned.append(propagated(pinned.pin, pinned.p.blob("docs/note-001.md")))
    assert failures(pinned) == []
    _drop_last_verdict(pinned)
    (pinned.root / "docs" / "note-001.md").unlink()
    pinned.append(propagated(pinned.pin, "absent"))
    assert failures(pinned) == []


def test_a_verdict_that_does_not_describe_the_drift_does_not_silence_it(pinned):  # noqa: F811
    """A committed drift, and a verdict naming a well-formed object id the artifact has
    never been. `validate` refuses the unreadable values; this is the readable one, and
    the only thing that separates it from a discharge is whether the record is true."""
    pinned.note(NOTE.replace("0.04", "0.09"))
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "remeasure")
    ((outcome, _, _),) = pinned.outcomes()
    assert outcome == "flag", "the control: the drift is there to be silenced"

    pinned.append(propagated(pinned.pin, "b" * 40))
    still = pinned.outcomes()
    assert [o for o, _, _ in still] == ["flag"], "a live drift went silent"
    assert "has moved" in still[0][2]


def test_a_verdict_recording_the_pins_own_blob_does_not_silence_a_drift(pinned):  # noqa: F811
    """The value a forger reaches for without running anything, because it is the one they
    can read off the repository. The artifact as the pin has it is not a drift, whatever
    else is true of it."""
    at_pin = pinned.p.blob("docs/note-001.md")
    pinned.note(NOTE.replace("0.04", "0.09"))
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "remeasure")
    pinned.append(propagated(pinned.pin, at_pin))
    assert [o for o, _, _ in pinned.outcomes()] == ["flag"]


def test_a_staged_drift_edited_again_before_the_commit_does_not_wedge(pinned):  # noqa: F811
    """The whole sequence, as a person doing ordinary work produces it: stage a drift, let
    the hook discharge it, stage one more edit — `git add -p`, an amend, a formatter — and
    commit. Then put the ground back, which is a thing people do, and the ledger must not
    be left in a state no edit can repair."""
    original = (pinned.root / "docs" / "note-001.md").read_bytes()

    pinned.note(NOTE.replace("0.04", "0.09"))
    pinned.p.git("add", "-A")
    pinned.p.cl("freshness", "--cached", "--write")

    pinned.note(NOTE.replace("0.04", "0.11"))
    pinned.p.git("add", "-A")
    pinned.p.cl("freshness", "--cached", "--write")
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "the remeasurement, and the ledger that says so")

    (pinned.root / "docs" / "note-001.md").write_bytes(original)
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "put it back")

    # The ground is fresh again and the two verdicts record sections this run does not
    # see: nothing can confirm them and nothing can refute them. A flag, not a failure —
    # the entry is contested with no reading, so a reading is owed, and the flag says so
    # without wedging the commit.
    got = pinned.outcomes()
    assert [o for o, _, _ in got] == ["flag"], got
    assert "nothing can confirm it and nothing can refute it" in got[0][2]
    assert pinned.p.cl("check") == 0


def test_the_orphan_rule_still_refuses_a_ground_no_verdict_caused(pinned):  # noqa: F811
    """The control for the rule that un-wedges it. Asking the question of the ground
    rather than of each verdict must not become "one verdict excuses the rest": with no
    caused verdict among them, two verdicts recording the blob the pin already has are
    still an orphan, and the report names both."""
    at_pin = pinned.p.digest("docs/note-001.md", "Observation")
    pinned.append(propagated(pinned.pin, at_pin))
    pinned.append(propagated(pinned.pin, at_pin))
    ((part, message),) = failures(pinned, checker=freshness)
    assert part == "Verdicts"
    assert "verdicts 1, 2" in message
    assert "orphan" in message


def test_a_forged_verdict_is_named_even_beside_a_caused_sibling(pinned):  # noqa: F811
    """QE8-85. Asking the question of the ground bought the forger nothing — a caused
    sibling already discharges every later drift of that ground, so the masked verdict
    adds no suppression — but the first version of the rule stopped *reporting* it, and
    the report was the rule's only diagnostic. A verdict recording the pin's own blob is
    refutable whatever stands beside it, and no run of this checker writes one, so there
    is no honest flow for the accusation to wedge."""
    at_pin = pinned.p.digest("docs/note-001.md", "Observation")
    pinned.append(propagated(pinned.pin, at_pin))
    pinned.note(NOTE.replace("0.04", "0.09"))
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "a real drift, really discharged")
    pinned.append(propagated(pinned.pin, pinned.p.digest("docs/note-001.md", "Observation")))
    (pinned.root / "docs" / "note-001.md").write_text(NOTE, encoding="utf-8")
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "and back to what the pin has")

    ((part, message),) = failures(pinned, checker=freshness)
    assert part == "Verdicts"
    assert "verdict 1" in message and "verdict 2" not in message
    assert "states no drift" in message


def test_an_abandoned_pre_commit_discharge_does_not_wedge(pinned):  # noqa: F811
    """QE8-82. The whole sequence is documented workflow and an author who changed their
    mind: edit a note, run `freshness --write`, commit the ledger the way the docs say to,
    then undo the edit. The recorded section is not the one in front of the run, and
    unlike QE7-74's shape there is no second verdict to rescue the group, because
    `--write` appends nothing for a ground that is fresh.

    So the outcome is the lever rather than the branch: a record the checker cannot
    *confirm* is not the same thing as one it can *refute*, and reporting the first as a
    forgery is what made it a permanent red no legal edit could clear."""
    original = (pinned.root / "docs" / "note-001.md").read_bytes()
    pinned.note(NOTE.replace("0.04", "0.09"))
    assert pinned.p.cl("freshness", "--write") == 1
    pinned.p.git("add", "ledger")
    pinned.p.git("commit", "-qm", "the ledger says the ground moved")

    (pinned.root / "docs" / "note-001.md").write_bytes(original)
    ((outcome, part, message),) = pinned.outcomes()
    assert (outcome, part) == ("flag", "Verdicts"), "an abandoned edit wedges the entry"
    assert "nothing can confirm it and nothing can refute it" in message
    assert pinned.p.cl("check") == 0


def test_a_forged_discharge_is_not_laundered_by_a_no_op_commit(pinned):  # noqa: F811
    """Fixed. The defect, as this pass wrote it: ever_drifted() asks whether the artifact was
    ever touched since the pin, not whether this verdict was caused, so one no-op commit that
    edits the artifact and puts it back launders a pre-emptively written discharge permanently

    docs/FRESHNESS.md justifies the orphan rule as stopping a *pre-emptive* forgery:
    "Otherwise the discharge is forgeable by writing the verdict pre-emptively." The artifact
    here is byte-identical to the blob at the pin the whole way through. One commit touches
    it, the next puts it back, and nothing about the ground has changed.
    """
    forged = pinned.p.digest("docs/note-001.md", "Observation")
    pinned.append(FORGERY.format(pin=pinned.pin, artifact=forged))
    assert [o for o, _, _ in outcomes(pinned.root)] == ["fail"], (
        "the control: the forgery is caught while the artifact has never been touched"
    )

    note = pinned.root / "docs" / "note-001.md"
    original = note.read_bytes()
    note.write_bytes(original.replace(b"0.04", b"0.99"))
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "a touch")
    note.write_bytes(original)
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "and back again")
    assert note.read_bytes() == original

    assert [o for o, _, _ in outcomes(pinned.root)] == ["fail"], (
        "the ground is where the pin left it; the discharge names a drift that never "
        "happened and is still an orphan"
    )


def test_a_git_that_cannot_answer_does_not_retire_the_orphan_check(pinned, tmp_path, monkeypatch):  # noqa: F811
    """Fixed, twice over. The defect, as this pass wrote it: ever_drifted() read a git that
    could not answer as `it drifted`, so a rev-list that failed or timed out retired the
    forged-discharge check silently, with no report that it did not run. The rule then
    learned to say `could not be established`; and now it asks history nothing at all — a
    record is refuted against the anchor the pointer names and the tree in front of the
    run — so a `rev-list` that cannot answer has no way in. Kept as the control that it
    stays that way.
    """
    forged = pinned.p.digest("docs/note-001.md", "Observation")
    pinned.append(FORGERY.format(pin=pinned.pin, artifact=forged))
    assert [o for o, _, _ in outcomes(pinned.root)] == ["fail"], "the control"

    monkeypatch.setenv("PATH", f"{shim_git(tmp_path, 'rev-list')}{os.pathsep}{os.environ['PATH']}")
    got = outcomes(pinned.root)
    assert got, "a check that could not run is not a check that passed; this run said nothing"
    assert [o for o, _, _ in got] == ["fail"]


def test_an_edit_below_a_fence_inside_the_pinned_section_is_still_caught(project):
    """Fixed. The defect, as this pass wrote it: the same defect end to end — an edit below a
    fenced code block inside the pinned section is invisible to freshness and to resolve, so a
    claim's own evidence can be inverted with every checker green

    The severity of the one above. This is not a wording question: the sentence that is
    inverted is the one the claim rests on. The fence is in the note *at the pin*, so the only
    thing that changes afterwards is the conclusion below it.
    """
    note = project.root / "docs" / "note-001.md"
    note.write_text(FENCED_NOTE, encoding="utf-8")
    build(project, ['lab: docs/note-001.md § "Observation" @{pin}'])
    note.write_text(
        FENCED_NOTE.replace(
            "The error does not grow with degree.",
            "The error GROWS with degree, which is the claim inverted.",
        ),
        encoding="utf-8",
    )
    assert [o for o, _, _ in outcomes(project.root)] == ["flag"], (
        "the pinned section's own evidence was inverted and the checker said nothing"
    )


# === The residuals, held by something that goes red when they close ===================
#
# `docs/FRESHNESS.md` once stated these two as residuals of a discharge rule that asked
# history whether a recorded artifact was ever held. The rule asks history nothing now —
# a record either names the section in front of the run or it does not — and both
# residuals closed by deletion. They stay as the regressions for that.


TWO_SECTIONS = NOTE + "\n## Method\n\nStar graphs, one layer, sixteen dimensions.\n"


def test_a_blob_from_another_sections_edit_does_not_discharge_this_one(pinned):  # noqa: F811
    """The forger edits `## Method`, commits, and writes a discharge on `§ "Observation"`
    recording the object id the file now has — the whole file, which is what the old
    rule could find in history. A whole file's id names no section, so it describes no
    drift of this ground and discharges nothing; the pinned section was never touched,
    and when it really moves the flag is there."""
    pinned.note(TWO_SECTIONS)
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "a section the claim does not rest on")
    pinned.append(propagated(pinned.pin, pinned.p.blob("docs/note-001.md")))

    pinned.note(TWO_SECTIONS.replace("0.04", "0.09"))
    assert [o for o, _, _ in pinned.outcomes()] == ["flag"], (
        "the discharge silenced a real drift of the section it never described"
    )


def test_a_delete_and_restore_does_not_discharge_a_withdrawal(pinned):  # noqa: F811
    """`absent` needs no digest at all: `git rm`, commit, restore, commit, and the
    pre-emptively written discharge used to stand over every later drift of the ground,
    because the deletion was in the history. History is not asked now: `absent` records
    a ground that is gone, and a ground that is there and has moved is not that."""
    original = (pinned.root / "docs" / "note-001.md").read_bytes()
    pinned.append(propagated(pinned.pin, "absent"))
    pinned.p.git("rm", "-q", "docs/note-001.md")
    pinned.p.git("commit", "-qm", "gone")
    (pinned.root / "docs").mkdir(exist_ok=True)
    (pinned.root / "docs" / "note-001.md").write_bytes(original)
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "and back")

    pinned.note(NOTE.replace("0.04", "0.09"))
    assert [o for o, _, _ in pinned.outcomes()] == ["flag"], (
        "a delete-and-restore laundered a discharge into silencing a later drift"
    )
