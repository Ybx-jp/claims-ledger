"""What `resolve` makes of a ground whose anchor is stated by value.

An anchor by value names its datum in full, so resolving it is finding that text: in the
tree while the entry is still being written, and afterwards in the tree or in any version
of the path the repository holds. Every case here builds a real repository.
"""

import subprocess
import tempfile

import pytest

from claims_ledger import freshness, resolve
from claims_ledger.schema import open_ledger

NOTE = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.
"""


def reports(project, checker=resolve):
    return [(r.outcome, r.part, r.message) for r in checker.run(open_ledger(root=project.root))]


def entry_by_value(project, digest=None, section="Observation"):
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    digest = digest or project.digest("docs/note-001.md", "Observation")
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working',
        f'- lab: docs/note-001.md § "{section}" ={digest}',
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    return path


def commit_all(project, message):
    project.git("add", "-A")
    project.git("commit", "-qm", message)


def test_an_uncommitted_ground_must_digest_to_the_tree(project):
    project.git("init", "-q")
    entry_by_value(project, digest="sha256:" + "ab" * 32)
    ((outcome, part, message),) = reports(project)
    assert (outcome, part) == ("fail", "Grounds 1")
    assert "names text the working tree does not hold" in message
    assert "sha --write" in message


def test_an_uncommitted_ground_naming_a_missing_section_fails(project):
    project.git("init", "-q")
    entry_by_value(project, digest="sha256:" + "ab" * 32, section="Method")
    ((outcome, _, message),) = reports(project)
    assert outcome == "fail"
    assert "has no section 'Method'" in message


def test_a_ground_that_matches_the_tree_resolves_with_no_repository_asked(project):
    entry_by_value(project)  # no `git init`: nothing to be committed into
    assert reports(project) == []


def test_a_committed_ground_whose_text_moved_on_resolves_from_history(project):
    """The ordinary case after a commit: the section was edited, nobody has re-read it
    yet, freshness flags it, and resolve still finds the founding text one commit back."""
    project.git("init", "-q")
    entry_by_value(project)
    commit_all(project, "the claim, and the note it rests on")
    (project.root / "docs" / "note-001.md").write_text(
        NOTE.replace("0.04", "0.09"), encoding="utf-8"
    )
    assert reports(project) == []
    assert [o for o, _, _ in reports(project, freshness)] == ["flag"]


def test_history_is_searched_in_a_sha256_repository_too(project):
    """The same case as the sibling above, in a repository created with
    `--object-format=sha256`, where every object id git prints is sixty-four hex
    characters instead of forty.

    `blobs_since` collects the blob ids out of `git log --raw --no-abbrev` by matching
    them against `OBJECT_ID_RE`, which was forty-wide. In such a repository every id was
    filtered out, the set came back empty, and this ground — whose founding text is one
    commit back, exactly as above — was reported as held by no version of the file the
    repository has, blaming a rewritten history that had not happened. Narrowing the
    pattern back to `{40}` reddens this and leaves the sha1 sibling green, which is the
    pair that says the width was the whole of it.

    Measured before the widening: the immutability check, `sha --write`'s refusal on a
    committed entry, and a plain `check` over a clean ledger all worked in a sha256
    repository. This was the one false report, not a package that does not run there.
    """
    if not _sha256_repositories_are_supported():
        pytest.skip("this git cannot create a sha256 repository")
    project.git("init", "-q", "--object-format=sha256")
    entry_by_value(project)
    commit_all(project, "the claim, and the note it rests on")
    (project.root / "docs" / "note-001.md").write_text(
        NOTE.replace("0.04", "0.09"), encoding="utf-8"
    )
    assert reports(project) == []
    assert [o for o, _, _ in reports(project, freshness)] == ["flag"]


def _sha256_repositories_are_supported():
    with tempfile.TemporaryDirectory() as probe:
        return (
            subprocess.run(
                ["git", "init", "-q", "--object-format=sha256", probe],
                capture_output=True,
                check=False,
            ).returncode
            == 0
        )


def test_a_committed_ground_whose_text_no_version_holds_is_flagged(project):
    """The end state a rewritten history leaves: the entry is committed and its anchor
    digests to text no commit ever carried. A flag, not a failure — the datum is stated
    in full and freshness compares it as before; what is lost is the diff."""
    project.git("init", "-q")
    entry_by_value(project, digest="sha256:" + "ab" * 32)
    project.git("add", "-A")
    subprocess.run(
        ["git", "-C", str(project.root), "-c", "user.name=t", "-c", "user.email=t@e",
         "-c", "commit.gpgsign=false", "commit", "-qm", "landed past the hook"],
        check=True,
    )  # fmt: skip
    ((outcome, part, message),) = reports(project)
    assert (outcome, part) == ("flag", "Grounds 1")
    assert "no version of docs/note-001.md this repository holds" in message


def test_a_reading_moves_the_ground_past_text_that_is_gone(project):
    """The discharge: a by-value reading of the section as it now stands is what the
    ground is resolved from afterwards, so the flag does not outlive the repair."""
    project.git("init", "-q")
    path = entry_by_value(project, digest="sha256:" + "ab" * 32)
    project.git("add", "-A")
    subprocess.run(
        ["git", "-C", str(project.root), "-c", "user.name=t", "-c", "user.email=t@e",
         "-c", "commit.gpgsign=false", "commit", "-qm", "landed past the hook"],
        check=True,
    )  # fmt: skip
    assert [o for o, _, _ in reports(project)] == ["flag"]
    text = path.read_text(encoding="utf-8")
    head, marker, tail = text.partition("\n## References")
    now = project.digest("docs/note-001.md", "Observation")
    reading = (
        "- 2026-11-21T10:15:00-08:00 · corroborated · grade: measured · author: main\n"
        f'  evidence: lab: docs/note-001.md § "Observation" ={now}\n'
        "  note: re-read after the history was rewritten\n"
    )
    path.write_text(head.rstrip("\n") + "\n\n" + reading + marker + tail, encoding="utf-8")
    assert reports(project) == []
    assert reports(project, freshness) == []


def test_a_readings_own_evidence_is_not_read_out_of_anything(project):
    """A reading names the datum it read; a mistyped digest is a reading of text that is
    not there, which freshness reports as a moved ground, and resolve has nothing to read
    it out of."""
    project.git("init", "-q")
    path = entry_by_value(project)
    commit_all(project, "the claim")
    text = path.read_text(encoding="utf-8")
    head, marker, tail = text.partition("\n## References")
    reading = (
        "- 2026-11-21T10:15:00-08:00 · corroborated · grade: measured · author: main\n"
        '  evidence: lab: docs/note-001.md § "Observation" =sha256:' + "cd" * 32 + "\n"
        "  note: a reading that read nothing\n"
    )
    path.write_text(head.rstrip("\n") + "\n\n" + reading + marker + tail, encoding="utf-8")
    assert [o for o, _, _ in reports(project, freshness)] == ["flag"]
    # resolve finds no text for the reading in the tree or in history, and says so once,
    # for the ground the reading is compared from.
    ((outcome, part, _),) = reports(project)
    assert (outcome, part) == ("flag", "Grounds 1")


def test_a_shallow_clone_cannot_settle_whether_the_text_is_gone(project, tmp_path):
    project.git("init", "-q")
    entry_by_value(project)
    commit_all(project, "the claim, and the note it rests on")
    (project.root / "docs" / "note-001.md").write_text(
        NOTE.replace("0.04", "0.09"), encoding="utf-8"
    )
    commit_all(project, "remeasured, not yet re-read")
    clone = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{project.root}", str(clone)], check=True
    )
    got = [(r.outcome, r.message) for r in resolve.run(open_ledger(root=clone))]
    pin = [m for o, m in got if "Grounds" in m or "shallow" in m]
    assert any("shallow clone" in m for _, m in got), got
    assert not any("this repository holds digests" in m for _, m in got), got
    assert pin or got


def test_a_git_that_cannot_say_whether_the_entry_is_committed_is_a_failure(
    project, tmp_path, monkeypatch
):
    """The branch between `fail, recompute the digest` and `look in history` is whether
    git holds the entry, and a git that could not say is neither answer. `run()`'s own
    gate asks `rev-parse --git-dir` and nothing more, so a git broken only in the walk
    that lists what the repository holds passes it; read as `not committed`, that git
    would tell a person to recompute an anchor on an entry whose frozen region a commit
    already names.

    The shim breaks `--all`, which is the reach `committed_paths` asks over: every ref
    and every operation in progress. It used to break `--verify`, which is what the
    question was asked with while it was asked of HEAD alone."""
    import os

    from test_git_degradation import _shim_git_that_cannot

    project.git("init", "-q")
    entry_by_value(project)
    commit_all(project, "the claim, and the note it rests on")
    (project.root / "docs" / "note-001.md").write_text(
        NOTE.replace("0.04", "0.09"), encoding="utf-8"
    )
    assert reports(project) == []
    shim = _shim_git_that_cannot(tmp_path, "--all")
    monkeypatch.setenv("PATH", f"{shim}{os.pathsep}{os.environ['PATH']}")
    ((outcome, part, message),) = reports(project)
    assert (outcome, part) == ("fail", "Grounds 1")
    assert "whether A0001-fraction-law is committed could not be established" in message
    assert "sha --write" not in message
