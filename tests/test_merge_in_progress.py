"""What the checkers see while a conflicted merge is being resolved.

The commit is the gate: a ledger state that is already on a commit somewhere has been
through it, and the checkers have to be able to reach that content wherever it is. During
a merge, half of it is on `MERGE_HEAD` and not on `HEAD`, and a checker that asks git only
about `HEAD` sees a ledger that is missing everything the incoming side brought.

Both tests below drive a real conflicted merge rather than simulating one, because what is
being tested is which revisions git is asked about, and a fixture that stood in for the
merge would be asserting the thing it replaced.
"""

import subprocess

import pytest

from claims_ledger import open_ledger, resolve, validate

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
