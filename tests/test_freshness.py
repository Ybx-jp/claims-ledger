"""The freshness checker: a pinned ground still names the artifact it was established on.

Every case here builds a real repository and makes a real commit. The checker's whole
subject is what git says about two revisions of a file, so a test that stubbed git would
prove nothing about the thing being claimed.

The specification is docs/FRESHNESS.md.
"""

import os
import subprocess

import pytest

from claims_ledger import freshness, references, resolve, validate
from claims_ledger.schema import open_ledger

NOTE = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.
"""


class Pinned:
    """A project whose entry rests on `docs/note-001.md` at a commit that exists."""

    def __init__(self, project, pin):
        self.p = project
        self.pin = pin
        self.root = project.root

    def ledger(self):
        return open_ledger(root=self.root)

    def run(self, write=False):
        return freshness.run(self.ledger(), write=write)

    def note(self, text):
        (self.root / "docs" / "note-001.md").write_text(text, encoding="utf-8")

    def entry_path(self):
        return next(self.p.entries.glob("A0001-*.md"))

    def append(self, block):
        """Append below the marker, the way a person or the machinery would."""
        path = self.entry_path()
        text = path.read_text(encoding="utf-8")
        head, marker, tail = text.partition("\n## References")
        path.write_text(head.rstrip("\n") + "\n\n" + block + marker + tail, encoding="utf-8")

    def outcomes(self, write=False):
        return [(r.outcome, r.part, r.message) for r in self.run(write=write)]


@pytest.fixture
def pinned(project):
    """The artifact is committed first, so the entry can name the commit it rests on;
    then the entry is committed, so its frozen region has a blob to be held to."""
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the artifact, before any claim rests on it")
    pin = _head(project)
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    text = path.read_text(encoding="utf-8").replace(
        'lab: docs/note-001.md § "Observation" @working',
        f'lab: docs/note-001.md § "Observation" @{pin}',
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    return Pinned(project, pin)


def _head(project):
    """The short object id of HEAD, which is what a person writing a pin would copy."""
    out = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


# --- the three findings ---------------------------------------------------------------


def test_an_untouched_ground_is_fresh(pinned):
    assert pinned.outcomes() == []


def test_a_committed_edit_is_a_moved_ground(pinned):
    pinned.note(NOTE.replace("0.04", "0.09"))
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "remeasure")
    ((outcome, part, message),) = pinned.outcomes()
    assert outcome == "flag"
    assert part == "Grounds 1"
    assert "has moved" in message
    assert "1 commit has touched section 'Observation'" in message


def test_an_uncommitted_edit_is_already_a_moved_ground(pinned):
    """The comparison is against the working tree, not HEAD. In a pre-commit hook HEAD is
    still the commit before the edit being made, and a HEAD comparison would surface the
    drift one commit late, against a diff the author has stopped thinking about."""
    pinned.note(NOTE.replace("0.04", "0.09"))
    ((outcome, _, message),) = pinned.outcomes()
    assert outcome == "flag"
    assert "has moved" in message


def test_a_deleted_ground_is_withdrawn_and_fails(pinned):
    (pinned.root / "docs" / "note-001.md").unlink()
    ((outcome, part, message),) = pinned.outcomes()
    assert outcome == "fail"
    assert part == "Grounds 1"
    assert "is not in the working tree" in message


ROOT_USER = os.geteuid() == 0


TWO_SECTION_NOTE = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.

## Method

One layer, mean aggregation, sixteen dimensions.
"""


def test_two_grounds_on_one_artifact_are_two_questions(project):
    """`freshness` asks git about a pointer once per run and remembers the answer. The
    key is the whole pointer and not its target, and this is the difference: an entry may
    rest on two sections of one file, and a target-keyed memo answers the second with the
    first one's verdict — silently, with the suite and the corpus green. This
    repository's own L0010 is that shape. (docs/audits/ARCH-AUDIT.md finding 4, QE13-2.)
    """
    (project.root / "docs" / "note-001.md").write_text(TWO_SECTION_NOTE, encoding="utf-8")
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the artifact")
    pin = _head(project)
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            'lab: docs/note-001.md § "Observation" @working',
            f'lab: docs/note-001.md § "Observation" @{pin}\n'
            f'- lab: docs/note-001.md § "Method" @{pin}',
        ),
        encoding="utf-8",
    )
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    p = Pinned(project, pin)
    assert p.outcomes() == [], "precondition: both grounds are fresh"

    (project.root / "docs" / "note-001.md").write_text(
        TWO_SECTION_NOTE.replace("sixteen", "thirty-two"), encoding="utf-8"
    )
    ((outcome, part, message),) = p.outcomes()
    assert outcome == "flag", message
    assert part == "Grounds 2", "the second ground moved; the first names a section nobody edited"
    assert "'Method'" in message


@pytest.mark.skipif(ROOT_USER, reason="root ignores the permission bits under test")
def test_an_artifact_nobody_can_read_is_not_a_ground_that_moved(pinned):
    """`chmod 000` on the artifact came back as `has moved`, at exit 0, with a message
    naming a section it had not read: git lists a file it cannot open as changed, and
    `scoped()` mapped a text it could not get to onto the finding for a text that
    differs. The class this checker already has for a comparison that did not happen is
    `unknown`, and this was that, misfiled. (docs/audits/ARCH-AUDIT.md, finding 2.)
    """
    note = pinned.root / "docs" / "note-001.md"
    os.chmod(note, 0o000)
    try:
        ((outcome, part, message),) = pinned.outcomes()
    finally:
        os.chmod(note, 0o644)
    assert outcome == "fail", message
    assert part == "Grounds 1"
    assert "was not checked" in message
    assert "cannot be read" in message
    assert "has moved" not in message


@pytest.mark.skipif(ROOT_USER, reason="root ignores the permission bits under test")
def test_an_artifact_nobody_can_read_under_a_plain_pin_is_not_a_ground_that_moved(project):
    """The same, one branch over: a pointer with no section never reads the artifact at
    all, so the answer is git's `diff` — and git reports a file it cannot open as
    modified. Both branches now ask whether the bytes were reachable before they call it
    a change."""
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the artifact")
    pin = _head(project)
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    text = path.read_text(encoding="utf-8").replace(
        'lab: docs/note-001.md § "Observation" @working',
        f"experiment: docs/note-001.md @{pin}",
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")

    note = project.root / "docs" / "note-001.md"
    os.chmod(note, 0o000)
    try:
        reports = freshness.run(open_ledger(root=project.root))
    finally:
        os.chmod(note, 0o644)
    ((outcome, message),) = [(r.outcome, r.message) for r in reports]
    assert outcome == "fail", message
    assert "was not checked" in message
    assert "cannot be read" in message


@pytest.mark.skipif(ROOT_USER, reason="root ignores the permission bits under test")
def test_an_artifact_whose_directory_cannot_be_searched_is_not_a_withdrawn_ground(pinned):
    """One level above the file: `path.is_file()` was the presence check, and it does not
    have two answers where three are needed. With `docs/` unsearchable it raises
    PermissionError out of pathlib on 3.12 — `freshness` exited 2 having printed nothing
    and `check` printed four checkers and silently omitted the fifth — while 3.13 swallows
    the EACCES and answers False, which is a confident `withdrawn` for a file nobody could
    look at. Neither is an answer. (docs/audits/ARCH-AUDIT.md finding 2, QE11-4.)
    """
    docs = pinned.root / "docs"
    os.chmod(docs, 0o000)
    try:
        ((outcome, _, message),) = pinned.outcomes()
    finally:
        os.chmod(docs, 0o755)
    assert outcome == "fail", message
    assert "was not checked" in message
    assert "cannot be reached" in message
    assert "gone" not in message


def test_an_artifact_that_is_not_text_is_still_a_ground_that_moved(pinned):
    """The other half of the same branch, and the reason `unknown` is not the answer to
    every failed read: bytes that are there and are not UTF-8 are an artifact that really
    did change and simply cannot be narrowed to a section. `moved` is what the file-level
    comparison already said, and this must keep saying it."""
    (pinned.root / "docs" / "note-001.md").write_bytes(b"\xff\xfe not text at all\n")
    ((outcome, _, message),) = pinned.outcomes()
    assert outcome == "flag", message
    assert "has moved" in message


def test_a_branch_pin_is_unstable_and_the_drift_is_not_reported(pinned):
    """A pin that follows the work resolves forever, so it can never go stale. The
    checker says that once and does not then pretend to have compared anything."""
    # A name of this test's own choosing, never the checked-out branch: `git branch -f`
    # refuses to move the branch that is checked out, and which one that is depends on
    # the runner's `init.defaultBranch`.
    pinned.p.git("branch", "pinned-to-a-name", "HEAD")
    _repin(pinned, "pinned-to-a-name")
    pinned.note(NOTE.replace("0.04", "0.09"))
    outcomes = pinned.outcomes()
    assert [o for o, _, _ in outcomes] == ["flag"]
    assert "pinned to a name, not a commit" in outcomes[0][2]


def test_a_branch_whose_name_looks_like_an_object_id_is_still_unstable(pinned):
    """`beef` is four hex characters and a legal branch name. The shape of the text is
    not proof, so git is asked whether it is also a ref."""
    pinned.p.git("branch", "beef")
    _repin(pinned, "beef")
    outcomes = pinned.outcomes()
    assert [o for o, _, _ in outcomes] == ["flag"]
    assert "pinned to a name, not a commit" in outcomes[0][2]


# --- what is exempt -------------------------------------------------------------------


def test_an_unpinned_ground_is_not_this_checkers_business(pinned):
    """`@working` says in the schema that it is only as reproducible as the tree it was
    read in. There is no revision to compare against, so there is nothing to say."""
    _repin(pinned, "working")
    pinned.note(NOTE.replace("0.04", "0.09"))
    assert pinned.outcomes() == []


def test_a_fallen_entry_may_drift(pinned):
    """A fallen entry's Grounds are history: they record what it was established on, not
    what anyone should now believe."""
    pinned.append(
        "- 2026-11-20T09:00:00-08:00 · refuted · grade: measured · author: main\n"
        '  evidence: lab: docs/note-001.md § "Observation" @working\n'
        "  note: the sweep did not replicate\n"
    )
    pinned.note(NOTE.replace("0.04", "0.09"))
    assert pinned.outcomes() == []


def test_an_acknowledged_ground_is_silent(pinned):
    """A discharge names the artifact it was written about, and the artifact it names is
    the one in front of the run. Both halves matter: the `artifact:` line is what makes
    the verdict a discharge of *this* drift rather than of the pointer in general."""
    pinned.note(NOTE.replace("0.04", "0.09"))
    assert len(pinned.outcomes()) == 1
    pinned.append(
        "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
        f'  evidence: lab: docs/note-001.md § "Observation" @{pinned.pin}\n'
        f"  artifact: {pinned.p.blob('docs/note-001.md')}\n"
        "  note: propagated from a moved ground\n"
    )
    assert pinned.outcomes() == []


def _acknowledge(pinned, note="a reformat; the assertion is unaffected"):
    """The repair `docs/OPERATING.md` prescribes for an artifact that moved while the claim
    did not: the drift recorded by the machinery, committed, then a corroborating verdict
    naming the section as it now stands, committed. Returns the commit the reading names."""
    pinned.run(write=True)
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "the drift, recorded")
    read_at = _head(pinned.p)
    pinned.append(
        "- 2026-11-21T10:15:00-08:00 · corroborated · grade: measured · author: main\n"
        f'  evidence: lab: docs/note-001.md § "Observation" @{read_at}\n'
        f"  note: {note}\n"
    )
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "read again, and acknowledged")
    return read_at


def test_a_ground_is_compared_from_where_it_was_last_read(pinned):
    """A pin is frozen and a recorded drift is recorded for good, so the reference point
    has to be the thing that can advance: the corroborating verdict that re-read the
    section. Silent while nothing has changed since that reading; a change after it is
    news, and the flag says which reading it is news since."""
    pinned.note(NOTE.replace("0.04", "0.09"))
    read_at = _acknowledge(pinned)
    assert pinned.outcomes() == []
    pinned.note(NOTE.replace("0.04", "0.12"))
    ((outcome, part, message),) = pinned.outcomes()
    assert (outcome, part) == ("flag", "Grounds 1")
    assert "has moved" in message
    assert f"read last by verdict 2 at {read_at[:12]}" in message


def test_a_drift_after_a_reading_is_discharged_against_that_reading(pinned):
    """`--write` records the drift against the pointer it compared, so the next run finds
    the acknowledgement where it looks, and the orphan rule holds that verdict to the
    history since the reading rather than since the pin."""
    pinned.note(NOTE.replace("0.04", "0.09"))
    read_at = _acknowledge(pinned)
    pinned.note(NOTE.replace("0.04", "0.12"))
    pinned.run(write=True)
    verdicts = pinned.entry_path().read_text(encoding="utf-8").split("## Verdicts")[1]
    assert f'evidence: lab: docs/note-001.md § "Observation" @{read_at}' in verdicts
    assert pinned.outcomes() == []
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "the second drift, recorded")
    assert pinned.outcomes() == []


def test_a_reading_at_an_unpinned_reference_does_not_move_the_baseline(pinned):
    """A corroboration naming the section `@working` is a reading nothing can hold to a
    commit, so the ground is compared from its pin as before — and the drift recorded
    against the pin goes on discharging it."""
    pinned.note(NOTE.replace("0.04", "0.09"))
    pinned.run(write=True)
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "the drift, recorded")
    pinned.append(
        "- 2026-11-21T10:15:00-08:00 · corroborated · grade: measured · author: main\n"
        '  evidence: lab: docs/note-002.md § "Observation" @working\n'
        "  note: read elsewhere\n"
    )
    pinned.note(NOTE.replace("0.04", "0.12"))
    assert pinned.outcomes() == []


def test_a_forged_discharge_against_a_reading_is_still_an_orphan(pinned):
    """The orphan rule follows the baseline: a propagated verdict naming the reading's
    pointer but recording the artifact as that reading has it states no drift since it."""
    pinned.note(NOTE.replace("0.04", "0.09"))
    read_at = _acknowledge(pinned)
    pinned.append(
        "- 2026-11-22T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
        f'  evidence: lab: docs/note-001.md § "Observation" @{read_at}\n'
        f"  artifact: {pinned.p.blob('docs/note-001.md')}\n"
        "  note: propagated from a moved ground\n"
    )
    ((outcome, part, message),) = pinned.outcomes()
    assert (outcome, part) == ("fail", "Verdicts")
    assert "verdict 3" in message and "states no drift" in message


def test_a_verdict_naming_a_ground_that_has_not_drifted_is_an_orphan(pinned):
    """Without this the discharge is forgeable: write the verdict first and the ground
    never has to be looked at again.

    The forger records what the file is, because that is the value they can read off the
    repository without running anything — and the artifact as the pin has it states no
    drift, whatever else is true of it. That is the half of "not caused" git can refute,
    and it is the half that still fails."""
    pinned.append(
        "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
        f'  evidence: lab: docs/note-001.md § "Observation" @{pinned.pin}\n'
        f"  artifact: {pinned.p.blob('docs/note-001.md')}\n"
        "  note: propagated from a moved ground\n"
    )
    ((outcome, part, message),) = pinned.outcomes()
    assert outcome == "fail"
    assert part == "Verdicts"
    assert "states no drift" in message
    assert "orphan" in message


def test_a_verdict_naming_a_ground_the_entry_does_not_have_is_an_orphan(pinned):
    pinned.append(
        "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
        f'  evidence: lab: docs/nowhere.md § "Observation" @{pinned.pin}\n'
        "  note: propagated from a moved ground\n"
    )
    ((outcome, _, message),) = pinned.outcomes()
    assert outcome == "fail"
    assert "carries no such ground" in message


# --- writing --------------------------------------------------------------------------


def test_write_appends_a_verdict_and_still_fails(pinned):
    (pinned.root / "docs" / "note-001.md").unlink()
    outcomes = pinned.outcomes(write=True)
    # The withdrawn ground, and then the append itself: a run that changed a file in the
    # ledger exits non-zero so the appended text is looked at before it is committed.
    assert [o for o, _, _ in outcomes] == ["fail", "fail"]
    text = pinned.entry_path().read_text(encoding="utf-8")
    assert "author: propagation" in text
    assert "propagated from a withdrawn ground" in text
    # And the appended verdict discharges the finding on the next run.
    assert [o for o, _, _ in pinned.outcomes()] == []


def test_two_drifted_grounds_both_survive_one_write(project):
    """Each block is built from the entry's text as it was parsed, so two writes to one
    entry would make the second overwrite the first."""
    project.git("init", "-q")
    (project.root / "docs" / "note-002.md").write_text(NOTE, encoding="utf-8")
    project.git("add", "-A")
    project.git("commit", "-qm", "two artifacts")
    pin = _head(project)
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    text = path.read_text(encoding="utf-8").replace(
        'lab: docs/note-001.md § "Observation" @working',
        f'lab: docs/note-001.md § "Observation" @{pin}\n'
        f'- lab: docs/note-002.md § "Observation" @{pin}',
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")

    (project.root / "docs" / "note-001.md").unlink()
    (project.root / "docs" / "note-002.md").unlink()
    reports = freshness.run(open_ledger(root=project.root), write=True)
    assert [r.outcome for r in reports] == ["fail", "fail", "fail"]
    assert "appended 2 contested verdict(s)" in reports[-1].message
    text = path.read_text(encoding="utf-8")
    assert text.count("author: propagation") == 2
    assert freshness.run(open_ledger(root=project.root)) == []


# --- the seams with the other checkers ------------------------------------------------


def test_validate_accepts_the_verdict_freshness_writes(pinned):
    """The machinery writes two shapes now: propagate's entry: evidence, and this one."""
    (pinned.root / "docs" / "note-001.md").unlink()
    pinned.run(write=True)
    assert validate.run(pinned.ledger()) == []


def test_a_person_may_not_borrow_the_machines_name(pinned):
    """The widened rule is still a rule: an unpinned evidence pointer under the
    propagation author is a person writing under a check that did not run."""
    pinned.append(
        "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
        '  evidence: lab: docs/note-001.md § "Observation" @working\n'
        "  note: not something the machinery would write\n"
    )
    messages = [r.message for r in validate.run(pinned.ledger())]
    assert any("under the machine's name" in m for m in messages)


def test_the_contested_status_breaks_a_cites_as_live_citation(pinned):
    """Freshness needs no failure semantics of its own. It moves the status, and the
    citation checker does the rest — which is what makes a stale comment in a source file
    a broken build rather than a note nobody reads."""
    (pinned.root / "docs" / "digest.md").write_text(
        f"The law ({_entry_id(pinned)}, cites-as-live) still stands.\n", encoding="utf-8"
    )
    path = pinned.entry_path()
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.rstrip("\n") + "\n\n- docs/digest.md · standing · cites-as-live\n", encoding="utf-8"
    )
    assert references.run(pinned.ledger()) == []

    (pinned.root / "docs" / "note-001.md").unlink()
    pinned.run(write=True)
    messages = [r.message for r in references.run(pinned.ledger())]
    assert any("cites-as-live against A0001-" in m for m in messages)
    assert any("contested" in m for m in messages)


def test_pinned_grounds_with_no_repository_are_a_check_that_did_not_run(project):
    """Silence here would be the failure mode this package exists to refuse: a check that
    could not run, reported as a check that passed."""
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    text = path.read_text(encoding="utf-8").replace("@working", "@" + "a" * 40)
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    (report,) = freshness.run(open_ledger(root=project.root))
    assert report.outcome == "fail"
    assert "freshness did not run" in report.message


def _entry_id(pinned):
    return pinned.entry_path().stem


def _repin(pinned, new):
    path = pinned.entry_path()
    text = path.read_text(encoding="utf-8").replace(f"@{pinned.pin}", f"@{new}")
    path.write_text(text, encoding="utf-8")


def outcomes(root):
    return [(r.outcome, r.part, r.message) for r in freshness.run(open_ledger(root=root))]


def test_an_option_shaped_pin_is_not_reported_as_an_unstable_pin(pinned):
    r"""Fixed. The defect, as this pass wrote it: `git rev-parse --symbolic-full-name --upload-
    pack=x` exits 0 and echoes its own argument, which is git's parse-options behaviour for an
    unrecognised double-dash argument and not a refname; is_object_name() reads it as a
    symbolic ref, so an option-shaped pin gets an unstable-pin flag and resolve's `does not
    resolve` both — the two contradictory names LOW-36 was fixed to stop

    LOW-36's fix deleted OBJECT_NAME_RE and made git the arbiter for every pin. Pins are free
    text in the schema (`\S+`), so a pin beginning with a dash is a typo away, and git answers
    a question it was not asked.
    """
    path = pinned.entry_path()
    path.write_text(
        path.read_text(encoding="utf-8").replace(f"@{pinned.pin}", "@--upload-pack=x"),
        encoding="utf-8",
    )
    assert pinned.p.cl("sha", "--write", str(path)) == 0
    flags = [m for o, _, m in outcomes(pinned.root) if "can never go stale" in m]
    assert not flags, f"one defect under two contradictory names: {flags}"
    # `resolve.run()` answers with Reports, not the (outcome, part, message) triples
    # `outcomes()` builds above. Written as an unpack, this line raised TypeError instead
    # of asserting — reachable only once the flag above it stops firing, which is why the
    # xfail check the pass ran (fails for the reason it names) did not reach it.
    assert [r.outcome for r in resolve.run(open_ledger(root=pinned.root))].count("fail") == 1
