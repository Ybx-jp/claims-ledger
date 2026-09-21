"""What the checkers see when a ledger state is on a commit this branch cannot reach.

The commit is the gate: a ledger state that is already on a commit somewhere has been
through it, and the checkers have to be able to reach that content wherever it is. A
checker that asks git only about `HEAD` sees a ledger missing everything on every other
ref — during a merge, everything the incoming side brought; for a vendored ledger, its
whole history if the branch that committed it is not the one checked out.

Every fixture here drives real git rather than simulating it, because what is being tested
is which revisions git is asked about, and a fixture that stood in for the branch topology
would be asserting the thing it replaced. The preconditions are asserted in the fixtures
rather than in the tests. Two of these were `xfail(strict=True)` while #60 and #61 stood,
and the preconditions stayed in the fixtures when the markers came off: an xfail swallows
a broken fixture as readily as it swallows the defect it is there for, and a fixture that
has stopped building the state it names is no more use green than red.
"""

import subprocess

import pytest

from claims_ledger import open_ledger, resolve, validate
from claims_ledger.freshness import effective_pointer
from claims_ledger.schema import load_entries

NOTE = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.{tail}
"""


def git_may_fail(project, *args):
    """`Project.git` raises on a non-zero exit, and a conflicted merge exits 1 by design."""
    return subprocess.run(
        [
            "git",
            "-C",
            str(project.root),
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@example",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def entry_on_the_note(project, slug, tail):
    """An entry grounded in the Observation section of the shared note, with the note
    edited so that the two sides of the merge conflict there."""
    assert project.cl("new", slug) == 0
    path = next(project.entries.glob(f"*-{slug}.md"))
    project.write_full_entry(path)
    (project.root / "docs" / "note-001.md").write_text(NOTE.format(tail=tail), encoding="utf-8")
    # By value, not `@working`: the branch this is about is `resolve_by_value`, and the
    # fixture the conftest writes pins the note at `working`, which never reaches it.
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            '- lab: docs/note-001.md § "Observation" @working',
            '- lab: docs/note-001.md § "Observation" =?',
        ),
        encoding="utf-8",
    )
    assert project.cl("sha", "--write", str(path)) == 0
    assert "=sha256:" in path.read_text(encoding="utf-8")
    return path


@pytest.fixture
def conflicted_merge(project):
    """A project mid-merge: `ours` and `theirs` have each edited the note the entries rest
    on, and `theirs` carries an entry `ours` has never seen. Returns that entry's path."""
    project.git("init", "-q", "-b", "main")
    project.git("add", "-A")
    project.git("commit", "-q", "-m", "the project")

    project.git("checkout", "-q", "-b", "theirs")
    incoming = entry_on_the_note(project, "theirs", " Measured on the incoming side.")
    project.git("add", "-A")
    project.git("commit", "-q", "-m", "an entry only the incoming side has")

    project.git("checkout", "-q", "main")
    entry_on_the_note(project, "ours", " Measured on the receiving side.")
    project.git("add", "-A")
    project.git("commit", "-q", "-m", "an entry only the receiving side has")

    merge = git_may_fail(project, "merge", "theirs", "--no-edit")
    assert merge.returncode != 0, "the two sides were meant to conflict in the note"
    assert (project.root / ".git" / "MERGE_HEAD").is_file()
    # Resolve the conflict the way a person would: keep both sentences.
    (project.root / "docs" / "note-001.md").write_text(
        NOTE.format(tail=" Measured on the receiving side. Measured on the incoming side."),
        encoding="utf-8",
    )
    return project.entries / f"{incoming.name}"


def test_an_entry_the_incoming_side_committed_is_not_read_as_uncommitted(conflicted_merge, project):
    """`resolve` decides whether to search history at all from whether the entry is
    committed, and hard-fails when it is not — telling the author to run `sha --write`,
    which rewrites the Grounds. An entry on `MERGE_HEAD` is committed. Asking only `HEAD`
    makes the one state where a merge is being resolved the state where that advice is
    given about an entry whose frozen region is already in history."""
    ledger = open_ledger(str(project.root))
    said = [r for r in resolve.run(ledger) if r.outcome == "fail"]
    assert not any("is not committed" in r.message for r in said), (
        f"an entry on MERGE_HEAD was read as uncommitted: {[r.message for r in said]}"
    )


def test_the_frozen_region_of_an_incoming_entry_is_still_compared(conflicted_merge, project):
    """The quieter half. `validate` walks the history of the entries directory from HEAD,
    so mid-merge an incoming entry has no revisions, every comparison it feeds is skipped,
    and its frozen region is checked against nothing. It does not fail — it says nothing,
    which is the one report this package may not produce."""
    text = conflicted_merge.read_text(encoding="utf-8")
    assert "## Assertion" in text
    conflicted_merge.write_text(
        text.replace(
            "The mean aggregation error is governed by the stale fraction and not by degree.",
            "Something else entirely, edited above the append marker.",
        ),
        encoding="utf-8",
    )
    ledger = open_ledger(str(project.root))
    said = [r for r in validate.run(ledger) if r.outcome == "fail"]
    assert any("immutable" in r.message or "differs from the blob" in r.message for r in said), (
        f"the frozen region of an incoming entry was edited and nothing said so: "
        f"{[r.message for r in said]}"
    )


# --- a reading the incoming side committed (issue #61) -----------------------------------


@pytest.fixture
def reading_on_the_incoming_side(project):
    """A project mid-merge whose entry carries a ground pinned by reference and a
    `corroborated` reading pinned at a commit only the incoming side has.

    Returns `(the founding pin, the reading's pin)`. The merge is held open by a conflict
    in a third file: a branch that only appends a verdict to an entry auto-merges and
    commits, and there is then no mid-merge state to measure.
    """
    (project.root / "docs" / "note-001.md").write_text(NOTE.format(tail=""), encoding="utf-8")
    assert project.cl("new", "pinned") == 0
    path = next(project.entries.glob("*-pinned.md"))
    project.write_full_entry(path)

    project.git("init", "-q", "-b", "main")
    project.git("add", "-A")
    project.git("commit", "-q", "-m", "the project")
    founding = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            '- lab: docs/note-001.md § "Observation" @working',
            f'- lab: docs/note-001.md § "Observation" @{founding}',
        ),
        encoding="utf-8",
    )
    project.git("add", "-A")
    project.git("commit", "-q", "-m", "pin the ground by reference")

    project.git("checkout", "-q", "-b", "theirs")
    (project.root / "docs" / "note-001.md").write_text(
        NOTE.format(tail=" Re-measured on the incoming side."), encoding="utf-8"
    )
    project.git("add", "-A")
    project.git("commit", "-q", "-m", "the incoming side edits the note")
    reading = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    verdict = (
        "\n- 2026-09-20T10:00:00-07:00 · corroborated · grade: measured · author: main\n"
        f'  evidence: lab: docs/note-001.md § "Observation" @{reading}\n'
        "  note: re-read on the incoming side.\n"
    )
    text = path.read_text(encoding="utf-8")
    assert "## Verdicts\n" in text
    # Under `## Verdicts`, not appended to the file: a verdict written after
    # `## References` is not read as a verdict at all, and the probe then reports the
    # founding pin in both states and looks like a clean pass of the broken code.
    path.write_text(text.replace("## Verdicts\n", "## Verdicts\n" + verdict, 1), encoding="utf-8")
    project.git("add", "-A")
    project.git("commit", "-q", "-m", "a reading, on the incoming side")

    for branch, body in (("main", "ours\n"), ("theirs", "theirs\n")):
        project.git("checkout", "-q", branch)
        (project.root / "OTHER.md").write_text(body, encoding="utf-8")
        project.git("add", "-A")
        project.git("commit", "-q", "-m", f"{branch} edits a third file")
    project.git("checkout", "-q", "main")
    merge = git_may_fail(project, "merge", "theirs", "--no-edit")
    assert merge.returncode != 0, "the two sides were meant to conflict in the third file"
    assert (project.root / ".git" / "MERGE_HEAD").is_file()
    (project.root / "OTHER.md").write_text("resolved\n", encoding="utf-8")

    def effective():
        ledger = open_ledger(str(project.root))
        entry = load_entries(ledger)[0]
        q, _used = effective_pointer(entry, entry.ground_pointers[0], ledger.config, ledger.repo)
        return q.pin

    return founding, reading, effective


def test_a_reading_the_incoming_side_committed_still_sets_the_effective_pin(
    reading_on_the_incoming_side, project
):
    """A ground is compared from its latest reading, not from where it was founded. Which
    reading is latest cannot depend on whether a merge has been committed yet: the tree is
    the same either side of that commit, and so is the verdict list.

    Stated as the differential rather than as the mid-merge value, because asserting the
    value pins the bug — it would have to be rewritten by whoever fixes it, and a test that
    has to be rewritten to go green is not holding anything."""
    _founding, _reading, effective = reading_on_the_incoming_side
    mid_merge = effective()
    project.git("add", "-A")
    project.git("commit", "-q", "--no-edit")
    assert effective() == mid_merge, (
        "the effective pin changed when the merge was committed, and nothing about the "
        "entry or the tree changed with it"
    )


# --- a vendored ledger committed on another ref (issue #60) ------------------------------


@pytest.fixture
def vendored_on_another_ref(project, tmp_path):
    """A ledger in a subdirectory of somebody else's repository — so `<root>/.git` is
    absent and `enclosing_repository` is what finds its history — committed on a branch
    that is not the one checked out.

    Returns the entry's path, with its frozen region already drifted so that `sha --write`
    has something to restamp."""
    host = tmp_path
    assert not (project.root / ".git").exists(), "the ledger must not be its own repository"
    subprocess.run(["git", "-C", str(host), "init", "-q", "-b", "main"], check=True)
    (host / "HOST.md").write_text("the host project\n", encoding="utf-8")
    for args in (
        ["add", "HOST.md"],
        ["-c", "user.name=t", "-c", "user.email=t@e", "commit", "-q", "-m", "the host"],
    ):
        subprocess.run(["git", "-C", str(host), *args], check=True)

    assert project.cl("new", "vendored") == 0
    path = next(project.entries.glob("*-vendored.md"))
    project.write_full_entry(path)
    for args in (
        ["checkout", "-q", "-b", "side"],
        ["add", "-A"],
        ["-c", "user.name=t", "-c", "user.email=t@e", "commit", "-q", "-m", "vendor the ledger"],
        ["checkout", "-q", "main"],
        ["checkout", "side", "--", str(project.root.relative_to(host))],
    ):
        subprocess.run(["git", "-C", str(host), *args], check=True)

    rel = str(path.relative_to(host))
    on_head = subprocess.run(
        ["git", "-C", str(host), "log", "-1", "--format=%H", "--", rel],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    on_any = subprocess.run(
        ["git", "-C", str(host), "log", "-1", "--all", "--format=%H", "--", rel],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert not on_head, "precondition: HEAD's history does not name the entry"
    assert on_any, "precondition: some commit does"

    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "metric: mean L2 error of the aggregated representation",
            "metric: something else entirely, edited above the append marker",
        ),
        encoding="utf-8",
    )
    return path


def test_sha_write_refuses_a_vendored_entry_committed_on_another_ref(
    vendored_on_another_ref, project
):
    """What L0007 says must not happen, one ref over. The bytes are what is asserted and
    not the exit status: a fixed `sha --write` refuses by raising, which is a non-zero
    exit, but so is a dozen unrelated failures — and the thing that matters is whether the
    frozen region of an entry some commit already names came back changed."""
    before = vendored_on_another_ref.read_bytes()
    project.cl("sha", "--write", str(vendored_on_another_ref))
    assert vendored_on_another_ref.read_bytes() == before, (
        "the frozen region of an entry committed on another ref was rewritten"
    )
