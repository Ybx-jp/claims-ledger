"""The check between the fixer and the merge, and the five HIGHs it found in the sixth
pass's fixes.

The sixth pass argued against a seventh adversarial pass and for a gate on the fix
instead. The gate ran, changed nothing under `src/`, and returned five HIGH findings —
two of them in fix code one day old, three of them unreachable from a green 785-test
suite. This file is the regression for each, kept in the pass that found it the way
`test_pass6_regressions.py` is.

Two of the five are held elsewhere and are not repeated here: QE7-72's write funnel is in
`test_write_paths.py`, beside the funnel's other callers, and QE7-73 was a false number in
the fixer's own evidence rather than a defect in the package. What is here is the
`artifact:` line — the field the sixth pass's largest fix rests on, which until now no
code read in the state a discharge normally lives in, and which no checker held to a shape
at all.

Every case builds a real repository and makes real commits. Nothing patches git, the
filesystem or the package.
"""

from __future__ import annotations

from test_freshness import pinned  # noqa: F401  — the fixture, reused as-is

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


# === QE7-75 — the field no checker held to a shape ====================================
#
# `grep -n artifact src/claims_ledger/validate.py` returned nothing. A non-hex value, a
# wrong-case `absent`, two `artifact:` lines, and an `artifact:` on a hand-written verdict
# by a person all gave `validate: 0 failures` — in the commit that closed seven findings
# of exactly this class.


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
    by a person it claims a check that did not run."""
    pinned.append(
        "- 2026-11-20T09:00:00-08:00 · corroborated · grade: measured · author: main\n"
        "  evidence: experiment: docs/note-001.md @working\n"
        f"  artifact: {pinned.p.blob('docs/note-001.md')}\n"
        "  note: read again and it still says so\n"
    )
    assert any("claims a check that did not run" in m for _, m in failures(pinned))


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


# === QE7-70 — the field nothing read while the drift was live =========================
#
# `orphans()` asks about `artifact:` only once the ground looks fresh again, and the
# suppression rule matched a verdict to a ground by the pointer alone. So over a real,
# committed, ongoing drift a propagated verdict carrying any value at all silenced every
# checker at exit 0 — which is the one thing this checker promises never to happen.


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


# === QE7-74 — the wedge two of the sixth pass's fixes made between them ================
#
# `seen_at(cached=True)` records the *index* blob and `caused()` looks only at committed
# history, so a drift that is staged, discharged, and then staged again before the commit
# is made leaves a verdict naming an id no commit ever held. Once the ground came back the
# discharge was an orphan permanently: verdicts append and only append, and the pin above
# the marker is frozen, so no legal edit could clear it. MEDIUM-34's wedge, reopened on
# the flag path HIGH-57's fix had just made the installed hook's default.


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

    assert pinned.outcomes() == [], "the discharged ground is wedged: no legal edit clears it"
    assert pinned.p.cl("check") == 0


def test_the_orphan_rule_still_refuses_a_ground_no_verdict_caused(pinned):  # noqa: F811
    """The control for the rule that un-wedges it. Asking the question of the ground
    rather than of each verdict must not become "one verdict excuses the rest": with no
    caused verdict among them, two are still an orphan, and the report names both."""
    pinned.append(propagated(pinned.pin, "b" * 40))
    pinned.append(propagated(pinned.pin, "c" * 40))
    ((part, message),) = failures(pinned, checker=freshness)
    assert part == "Verdicts"
    assert "verdicts 1, 2" in message
    assert "orphan" in message


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
