"""The freshness checker held to `docs/FRESHNESS.md`, which is the oracle here.

Fifth-pass QE, the `freshspec` dimension. Every case builds a real repository and makes
real commits: the checker's whole subject is what git says about two revisions of a file,
so nothing here patches git, the filesystem or the package.

Each strict xfail names the sentence of the specification it holds the code to. The
controls beside them are not decoration — they are what keeps a fix from being a
weakening, and they record which surfaces were examined and found clean.
"""

import subprocess

import pytest

from claims_ledger import freshness, resolve, validate
from claims_ledger.schema import exit_code, open_ledger

NOTE = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.
"""

TWO_SECTIONS = NOTE + "\n## Method\n\nStar graphs, one layer, sixteen dimensions.\n"

NESTED = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.

### Detail

The sweep ran sixteen times and the error never exceeded 0.05.

## Method

Star graphs, one layer, sixteen dimensions.
"""


# --- the fixture shape ------------------------------------------------------------------


def rev(project, *args):
    out = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def build(project, grounds, pin=None):
    """An entry whose Grounds are `grounds` (pointer lines, `{pin}` substituted), over a
    repository whose artifacts were committed before the claim rested on them.

    Returns (entry path, pin). The artifacts are committed first so the entry can name a
    commit that exists; the entry is committed after, so its frozen region has a blob.
    """
    project.git("init", "-q")
    project.git("add", "-A")
    # `--allow-empty`, so that a caller that has already committed the artifacts itself —
    # to have a commit to name as the pin — can still call this.
    project.git("commit", "-qm", "the artifacts", "--allow-empty")
    pin = pin or rev(project, "--short", "HEAD")
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    lines = "\n".join("- " + g.format(pin=pin) for g in grounds)
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working', lines
    )
    assert text != path.read_text(encoding="utf-8")
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


def note(project, text, name="note-001.md"):
    (project.root / "docs" / name).write_text(text, encoding="utf-8")


def append(path, block):
    """Append below the marker, the way a person or the machinery would."""
    text = path.read_text(encoding="utf-8")
    head, marker, tail = text.partition("\n## References")
    path.write_text(head.rstrip("\n") + "\n\n" + block + marker + tail, encoding="utf-8")


def contested(pointer_line, note="propagated from a moved ground"):
    return (
        "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
        f"  evidence: {pointer_line}\n"
        f"  note: {note}\n"
    )


# --- the discharge, and what it discharges ----------------------------------------------


def test_a_verdict_naming_the_same_section_still_discharges_it(project):
    """The control for the next test: a verdict that names the drifted section is a
    discharge, and must stay one."""
    note(project, TWO_SECTIONS)
    path, pin = build(
        project,
        [
            'lab: docs/note-001.md § "Observation" @{pin}',
            'lab: docs/note-001.md § "Method" @{pin}',
        ],
    )
    note(project, TWO_SECTIONS.replace("0.04", "0.09"))
    assert [o for o, _, _ in outcomes(project)] == ["flag"]
    append(path, contested(f'lab: docs/note-001.md § "Observation" @{pin}'))
    assert outcomes(project) == []


@pytest.mark.xfail(
    strict=True,
    reason="BUG: has_acknowledged() compares type/target/pin and not section, so one "
    "verdict discharges every ground pointing at the same file and pin",
)
def test_a_verdict_naming_one_section_does_not_discharge_another(project):
    """`§ "<section>"` is part of a pointer's identity everywhere else in this checker —
    `scoped()` compares only that span, `orphans()` looks the pointer up by its raw text,
    the message names the section. A verdict naming one section must not silence the
    drift of another, or a drifted ground is fresh forever and no checker ever says so.
    """
    note(project, TWO_SECTIONS)
    path, pin = build(
        project,
        [
            'lab: docs/note-001.md § "Observation" @{pin}',
            'lab: docs/note-001.md § "Method" @{pin}',
        ],
    )
    note(project, TWO_SECTIONS.replace("0.04", "0.09").replace("sixteen", "thirty-two"))
    assert len(outcomes(project)) == 2
    append(path, contested(f'lab: docs/note-001.md § "Observation" @{pin}'))
    still = outcomes(project)
    assert [o for o, _, _ in still] == ["flag"]
    assert "'Method'" in still[0][2]


# --- --write and the exit code -----------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason="BUG: a --write run whose only findings are `moved` appends verdicts to the "
    "ledger and exits 0; docs/FRESHNESS.md requires the run to exit non-zero afterwards",
)
def test_write_over_a_moved_ground_still_exits_non_zero(project):
    """docs/FRESHNESS.md: "so `freshness --write` appends it, and — following `propagate`
    — the run still exits non-zero afterwards so the appended text is looked at before it
    is committed." `propagate` gets this for free because every block it queues is queued
    beside a `fail`; freshness queues the moved case beside a `flag`."""
    path, _ = build(project, ["experiment: docs/note-001.md @{pin}"])
    note(project, NOTE.replace("0.04", "0.09"))
    reports = freshness.run(open_ledger(root=project.root), write=True)
    assert path.read_text(encoding="utf-8").count("author: propagation") == 1
    assert exit_code(reports) == 1


def test_write_over_a_withdrawn_ground_exits_non_zero(project):
    """The control. `withdrawn` is a `fail`, so this path already obeys the rule — which
    is why the existing suite did not catch the `moved` one."""
    path, _ = build(project, ["experiment: docs/note-001.md @{pin}"])
    (project.root / "docs" / "note-001.md").unlink()
    reports = freshness.run(open_ledger(root=project.root), write=True)
    assert path.read_text(encoding="utf-8").count("author: propagation") == 1
    assert exit_code(reports) == 1


def test_a_second_write_does_not_duplicate_the_verdict(project):
    """The appended verdict discharges the finding, so nothing is queued the second time."""
    path, _ = build(project, ["experiment: docs/note-001.md @{pin}"])
    note(project, NOTE.replace("0.04", "0.09"))
    freshness.run(open_ledger(root=project.root), write=True)
    assert outcomes(project, write=True) == []
    assert path.read_text(encoding="utf-8").count("author: propagation") == 1


# --- section scoping under the shipped default pattern -----------------------------------


def test_an_edit_directly_under_the_named_heading_is_still_caught(project):
    """The control for the next test. Text between `## Observation` and the first thing
    that ends it is inside the section and must stay inside it."""
    note(project, NESTED)
    build(project, ['lab: docs/note-001.md § "Observation" @{pin}'])
    note(project, NESTED.replace("the measured error was 0.04", "the measured error was 0.31"))
    ((outcome, part, message),) = outcomes(project)
    assert (outcome, part) == ("flag", "Grounds 1")
    assert "section 'Observation'" in message


@pytest.mark.xfail(
    strict=True,
    reason="BUG: the default section pattern's terminator `^#+` matches a heading at any "
    "depth, so a `###` subsection ends its parent `##` section and everything under it "
    "is outside the comparison",
)
def test_an_edit_under_a_subheading_of_the_named_section_is_a_moved_ground(project):
    """docs/FRESHNESS.md documents the anchoring caveat for a *configured* pattern and
    says to "anchor at the granularity the section really has". The shipped Markdown
    default cannot be anchored that way — `#+` is every depth — and nested headings are
    the ordinary shape of a lab note. The claim's own evidence can be inverted under a
    `###` and every checker stays green.
    """
    note(project, NESTED)
    build(project, ['lab: docs/note-001.md § "Observation" @{pin}'])
    note(project, NESTED.replace("never exceeded 0.05", "exceeded 0.05 in every run"))
    reported = outcomes(project)
    assert [o for o, _, _ in reported] == ["flag"], "the edit was inside the named section"
    assert reported[0][1] == "Grounds 1"
    assert "section 'Observation'" in reported[0][2]


def test_a_duplicated_heading_compares_only_the_first(project):
    """Recorded rather than assumed. `section_span` takes the first match, so an edit to
    a second `## Observation` is not this ground's drift. `resolve` reads the same span,
    so the two checkers agree about which one the claim rests on — which is why this is
    a recorded shape and not a finding."""
    duplicated = NOTE + "\n## Observation\n\nA second run gave 0.05.\n"
    note(project, duplicated)
    build(project, ['lab: docs/note-001.md § "Observation" @{pin}'])
    note(project, duplicated.replace("A second run gave 0.05", "A second run gave 0.50"))
    assert outcomes(project) == []
    # And the first copy is still compared.
    note(project, duplicated.replace("0.1 the measured error was 0.04", "0.2 it was 0.11"))
    assert [o for o, _, _ in outcomes(project)] == ["flag"]


# --- what a pin is -----------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason="BUG: OBJECT_NAME_RE is lowercase-only, so an uppercase object id is reported "
    "as an unstable pin — git resolves it and resolve accepts it",
)
def test_an_uppercase_object_id_pin_is_not_a_name(project):
    """docs/FRESHNESS.md step 1: an unstable pin is one `git rev-parse
    --symbolic-full-name` names. Git resolves an uppercase object id and prints no
    refname for it, so the answer is `commit`. Reporting it as a name that "resolves
    forever and can never go stale" is false twice over."""
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the artifacts")
    upper = rev(project, "HEAD").upper()
    assert (
        subprocess.run(
            ["git", "-C", str(project.root), "rev-parse", "--verify", "--quiet", upper],
            capture_output=True,
            check=False,
        ).returncode
        == 0
    ), "this test's premise: git itself resolves an uppercase object id"
    build(project, ["experiment: docs/note-001.md @{pin}"], pin=upper)
    assert resolve.run(open_ledger(root=project.root)) == []
    assert outcomes(project) == []


@pytest.mark.xfail(
    strict=True,
    reason="BUG: an uppercase object id is short-circuited as an unstable pin, so the "
    "artifact behind it is never compared at all — a deleted ground is never reported",
)
def test_a_withdrawn_ground_under_an_uppercase_pin_is_still_reported(project):
    """The severity of the previous test. `drift()` reports and stops for an unstable
    pin, so the flag is not merely wrong wording: the ground is never looked at."""
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the artifacts")
    build(project, ["experiment: docs/note-001.md @{pin}"], pin=rev(project, "HEAD").upper())
    (project.root / "docs" / "note-001.md").unlink()
    assert [o for o, _, _ in outcomes(project)] == ["fail"]


@pytest.mark.xfail(
    strict=True,
    reason="BUG: a non-hex pin that names nothing is reported as an unstable pin, so one "
    "defect is reported under two names — resolve already fails it as unresolvable",
)
def test_a_named_pin_that_names_nothing_is_not_an_unstable_pin(project):
    """docs/FRESHNESS.md step 1: "`git rev-parse --symbolic-full-name <pin>` — **non-empty
    output** means unstable pin". For `v9.9` git prints nothing and exits non-zero, so
    the pin is not a symbolic ref; it is a pointer that does not resolve, which step 2
    hands to `resolve`. `drift()`'s own docstring refuses to report one defect twice, and
    the equivalent hex pin (`@deadbeef`) is correctly silent here — this is the same
    question answered two different ways depending on the shape of the text.
    """
    build(project, ["experiment: docs/note-001.md @v9.9"], pin="v9.9")
    assert [r.outcome for r in resolve.run(open_ledger(root=project.root))] == ["fail"]
    assert outcomes(project) == []


def test_a_hex_pin_that_names_nothing_is_left_to_resolve(project):
    """The control, and the fourth pass's MEDIUM-27 disposition: `rev-parse --verify
    --quiet` exits 1 for a pin that is simply not there, which is git answering, not git
    failing. Freshness is silent and `resolve` reports it once."""
    build(project, ["experiment: docs/note-001.md @deadbeef"], pin="deadbeef")
    assert [r.outcome for r in resolve.run(open_ledger(root=project.root))] == ["fail"]
    assert outcomes(project) == []


def test_an_annotated_tag_pin_is_an_unstable_pin(project):
    """The control on the other side: a tag really is a name that follows the work, and
    docs/FRESHNESS.md names "a branch or a tag" together."""
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the artifacts")
    project.git("tag", "-a", "v1.0", "-m", "release")
    build(project, ["experiment: docs/note-001.md @v1.0"], pin="v1.0")
    note(project, NOTE.replace("0.04", "0.09"))
    ((outcome, _, message),) = outcomes(project)
    assert outcome == "flag"
    assert "pinned to a name, not a commit" in message


# --- --cached ----------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason="BUG: freshness.run() takes no `cached` argument, so `check --cached` compares "
    "the working tree while the rest of the run reads the index; a staged drift the "
    "working tree does not carry is reported as 0 failures, 0 flags",
)
def test_cached_compares_the_index_not_the_working_tree(project, capsys):
    """docs/FRESHNESS.md, "The comparison, exactly", step 3: "The artifact as this run
    reads it: `git hash-object <path>` on the working tree, **or the index blob under
    `--cached`, matching whatever the rest of the run is reading**."

    Partial staging is the ordinary way to reach this state: the edit is in the index and
    the working tree has been put back. What the commit will contain is what `--cached`
    is for, and it is the one thing this run does not look at.
    """
    build(project, ["experiment: docs/note-001.md @{pin}"])
    note(project, NOTE.replace("0.04", "0.09"))
    project.git("add", "docs/note-001.md")
    note(project, NOTE)  # the index carries the drift; the working tree does not
    assert (
        subprocess.run(
            ["git", "-C", str(project.root), "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        == "docs/note-001.md"
    ), "this test's premise: the drift is staged"
    project.cl("check", "--cached")
    assert "has moved" in capsys.readouterr().out


def test_check_without_cached_reads_the_working_tree(project, capsys):
    """The control. Without `--cached` the working tree is the right subject, and it is
    read — which is the pre-commit-hook argument docs/FRESHNESS.md makes for comparing
    against the working tree rather than HEAD."""
    build(project, ["experiment: docs/note-001.md @{pin}"])
    note(project, NOTE.replace("0.04", "0.09"))
    project.cl("check")
    assert "has moved" in capsys.readouterr().out


# --- the orphan rule ---------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason="BUG: undoing the edit that caused a discharge turns the discharge into an "
    "orphan failure that no legal edit can clear — removing the verdict fails the "
    "append-only check",
)
def test_a_reverted_drift_does_not_wedge_the_ledger(project):
    """docs/FRESHNESS.md justifies the orphan rule as stopping a *pre-emptive* forgery:
    "Otherwise the discharge is forgeable by writing the verdict pre-emptively." A
    verdict the checker itself wrote, because the ground had drifted, is not a forgery.

    The trap is that there is no way out. Verdicts append and only append, so the
    verdict cannot be removed; the entry's Grounds are frozen, so the pin cannot be
    changed. `check` exits 1 for the life of the entry.
    """
    path, _ = build(project, ["experiment: docs/note-001.md @{pin}"])
    note(project, NOTE.replace("0.04", "0.09"))
    freshness.run(open_ledger(root=project.root), write=True)
    project.git("add", "-A")
    project.git("commit", "-qm", "remeasure, and the discharge the checker wrote")
    assert outcomes(project) == []
    note(project, NOTE)  # the edit is undone
    assert outcomes(project) == []
    assert path.read_text(encoding="utf-8").count("author: propagation") == 1


def test_removing_the_orphaned_verdict_is_itself_a_failure(project):
    """Why the one above is a wedge and not an inconvenience. Recorded as a control: the
    append-only guarantee is correct and must not be relaxed to make room for a fix."""
    path, _ = build(project, ["experiment: docs/note-001.md @{pin}"])
    note(project, NOTE.replace("0.04", "0.09"))
    freshness.run(open_ledger(root=project.root), write=True)
    project.git("add", "-A")
    project.git("commit", "-qm", "remeasure, and the discharge the checker wrote")
    note(project, NOTE)
    assert [o for o, _, _ in outcomes(project)] == ["fail"]
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text[: text.index("- 20", text.index("## Verdicts"))] + text[text.index("## References") :],
        encoding="utf-8",
    )
    messages = [r.message for r in validate.run(open_ledger(root=project.root))]
    assert any("verdicts append and only append" in m for m in messages)


def test_a_fallen_entry_carrying_a_discharge_is_not_an_orphan(project):
    """`run()` exempts a fallen entry's Grounds; `orphans()` does not exempt its Verdicts,
    but sees the ground still drifted and stays quiet. No double report, and the
    exemption does not leak into an accusation."""
    path, pin = build(project, ["experiment: docs/note-001.md @{pin}"])
    note(project, NOTE.replace("0.04", "0.09"))
    append(path, contested(f"experiment: docs/note-001.md @{pin}"))
    append(
        path,
        "- 2026-11-21T09:00:00-08:00 · refuted · grade: measured · author: main\n"
        f"  evidence: experiment: docs/note-001.md @{pin}\n"
        "  note: the sweep did not replicate\n",
    )
    assert outcomes(project) == []


# --- the pathspec the checker builds -----------------------------------------------------


def test_a_glob_metacharacter_in_a_path_is_still_compared(project):
    """`docs/note[1].md` reaches `git diff … -- <path>` as a pathspec, where `[1]` is a
    wildcard. Git's matching also tries the literal path, so the real artifact's drift is
    still found. Recorded so that a later `:(literal)` fix is held to keeping this."""
    note(project, NOTE, name="note[1].md")
    build(project, ["experiment: docs/note[1].md @{pin}"])
    assert outcomes(project) == []
    note(project, NOTE.replace("0.04", "0.09"), name="note[1].md")
    assert [o for o, _, _ in outcomes(project)] == ["flag"]


@pytest.mark.xfail(
    strict=True,
    reason="BUG: the artifact path is passed to `git diff` as a pathspec, so a different "
    "file matching it as a glob is reported as this ground's drift",
)
def test_a_decoy_matching_the_pathspec_glob_is_not_this_grounds_drift(project):
    """`docs/note1.md` is not `docs/note[1].md` and no claim rests on it. The checker
    reports the untouched ground as moved because git read the path as a wildcard. A
    checker whose flags fire over files nobody pinned is the noise floor
    docs/FRESHNESS.md spends a section arguing about.
    """
    note(project, NOTE, name="note[1].md")
    note(project, NOTE, name="note1.md")
    build(project, ["experiment: docs/note[1].md @{pin}"])
    note(project, NOTE.replace("0.04", "0.09"), name="note1.md")
    assert outcomes(project) == []


# --- one defect, one name ----------------------------------------------------------------


def test_a_section_absent_at_the_pin_is_resolves_finding(project):
    """`scoped()` returns None when the section was never at the pin, on the grounds that
    `resolve` reports it. Checked rather than assumed: it does, once, and `check` exits
    non-zero."""
    note(project, "# note 001\n\nnothing measured yet.\n")
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "before the section existed")
    pin = rev(project, "--short", "HEAD")
    note(project, NOTE)
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    path.write_text(
        path.read_text(encoding="utf-8").replace("@working", f"@{pin}"), encoding="utf-8"
    )
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")

    assert outcomes(project) == []
    ((outcome, message),) = [
        (r.outcome, r.message) for r in resolve.run(open_ledger(root=project.root))
    ]
    assert outcome == "fail"
    assert "has no section 'Observation'" in message
    assert project.cl("check") == 1


def test_a_pin_that_is_a_blob_not_a_commit_is_resolves_finding(project):
    """A pin naming a blob is a pointer that does not resolve, not a comparison git
    declined to make. It must not arrive as `unknown`, which would be a second name for
    the same defect."""
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the artifacts")
    blob = rev(project, "HEAD:docs/note-001.md")
    build(project, ["experiment: docs/note-001.md @{pin}"], pin=blob)
    assert outcomes(project) == []
    assert [r.outcome for r in resolve.run(open_ledger(root=project.root))] == ["fail"]


# --- the messages the specification prints -----------------------------------------------


def test_the_three_findings_say_what_they_are(project):
    """docs/FRESHNESS.md prints an example line for each of the three findings and the
    code's wording differs from all three. The code's is better in each case — a tag is
    not a branch, and `rev-list` counted commits touching the artifact rather than
    withdrawals — so this pins the code and the specification is what should move.
    """
    build(project, ["experiment: docs/note-001.md @{pin}"])
    note(project, NOTE.replace("0.04", "0.09"))
    project.git("add", "-A")
    project.git("commit", "-qm", "remeasure")
    ((_, _, moved),) = outcomes(project)
    assert "has moved: 1 commit has touched it since the pin" in moved

    (project.root / "docs" / "note-001.md").unlink()
    ((outcome, _, withdrawn),) = outcomes(project)
    assert outcome == "fail"
    assert "is not in the working tree; the ground it names is gone" in withdrawn
    assert "1 commit has touched the artifact since the pin" in withdrawn
