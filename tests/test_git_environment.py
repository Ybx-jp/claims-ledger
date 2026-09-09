"""Every git call this package makes is about the repository it names with `-C`.

The environment can say otherwise. git reads a dozen variables that answer "which
repository, and where are its parts", and under any of them a `-C <somewhere>` is not the
question it looks like — which turns a check that did not happen into a check that
passed. Measured on git 2.43.0 before the scrub reached past discovery: with `GIT_DIR`,
`GIT_COMMON_DIR` or `GIT_OBJECT_DIRECTORY` naming any other repository, `sha --write`
rewrote the frozen region of an entry a commit already held and exited 0, and `validate`
dropped both immutability failures with nothing said. (docs/audits/ARCH-AUDIT.md, QE12-2.)

The one question this package really does ask of the environment is which index a commit
is being built in, and the tests for both directions are here: scrubbing `GIT_INDEX_FILE`
from a `--cached` read is the same false pass pointed the other way, because a partial
commit's index is not `.git/index`.

`tests/test_failure_paths.py` holds the sibling family — the discovery walk, which asks
the filesystem rather than git and so was never the environment's to answer.
"""

import os
import subprocess

import pytest
from test_freshness import pinned  # noqa: F401  — the fixture, reused as-is

FROZEN_EDIT = (
    "metric: mean L2 error of the aggregated representation",
    "metric: rewritten after the commit",
)


@pytest.fixture
def committed(project):
    """A project whose one entry a commit already holds, filled in so that every checker
    passes over it: the state `sha --write` refuses to restamp, and the one where an exit
    code from `validate` is about the frozen region and not about a scaffold."""
    project.cl("new", "stale-fraction-governs-error")
    path = project.write_full_entry(project.entry("A0001-stale-fraction-governs-error.md"))
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the entry as first written")
    return project, path


def elsewhere_repository(tmp_path, name="elsewhere"):
    """Another repository, with a commit in it, for a variable to point at."""
    other = tmp_path / name
    other.mkdir()
    subprocess.run(["git", "-C", str(other), "init", "-q"], check=True)
    (other / "x.txt").write_text("x\n", encoding="utf-8")
    for args in (
        ["add", "-A"],
        ["-c", "user.name=t", "-c", "user.email=t@e", "commit", "-qm", "x"],
    ):
        subprocess.run(["git", "-C", str(other), *args], check=True, capture_output=True)
    return other


def partial_index(project, *paths):
    """The index `git commit -- <path>` builds and hands the hook in `GIT_INDEX_FILE`:
    HEAD, plus the working tree's version of the named paths. Built here rather than
    provoked out of a real partial commit, because a hook that fails is a commit that does
    not happen, and these tests need to run the checkers themselves."""
    index = project.root / ".git" / "next-index-fixture.lock"
    env = {**os.environ, "GIT_INDEX_FILE": str(index)}
    for args in (["read-tree", "HEAD"], ["add", "--", *(str(p) for p in paths)]):
        subprocess.run(["git", "-C", str(project.root), *args], check=True, env=env)
    return index


def drift_the_frozen_region(path):
    text = path.read_text(encoding="utf-8")
    assert FROZEN_EDIT[0] in text
    path.write_text(text.replace(*FROZEN_EDIT), encoding="utf-8")


@pytest.mark.parametrize(
    "variable, value",
    [
        ("GIT_DIR", "{other}/.git"),
        ("GIT_COMMON_DIR", "{other}/.git"),
        ("GIT_OBJECT_DIRECTORY", "{other}/.git/objects"),
        ("GIT_WORK_TREE", "{other}"),
        ("GIT_ALTERNATE_OBJECT_DIRECTORIES", "{other}/.git/objects"),
        ("GIT_INDEX_FILE", "{other}/.git/index"),
        ("GIT_NAMESPACE", "somewhere"),
        ("GIT_CEILING_DIRECTORIES", "{other}"),
    ],
)
def test_sha_write_still_refuses_a_committed_entry_under_a_redirected_git(
    committed, tmp_path, capsys, monkeypatch, variable, value
):
    """The false pass, in the form it was measured. `sha --write` asks git whether this
    entry is already committed; under a variable that points git at another repository
    the answer came back `no`, and the frozen region of a committed entry was rewritten
    at exit 0 — L0007 not holding, silently, with nothing in the output to look at.

    Every variable in `GIT_REPOSITORY_ENV` is parametrized here, not only the three that
    were measured to bite: which ones reroute what is a property of the git version, and
    the rule this holds is that none of them is consulted. Deleting the scrub from
    `git_env()` reddens the first three.
    """
    project, path = committed
    other = elsewhere_repository(tmp_path)
    monkeypatch.setenv(variable, value.format(other=other))
    before = path.read_text(encoding="utf-8")
    drift_the_frozen_region(path)
    capsys.readouterr()
    assert project.cl("sha", "--write", str(path)) == 2
    assert "is committed" in capsys.readouterr().err
    assert path.read_text(encoding="utf-8") == before.replace(*FROZEN_EDIT)


def test_validate_reads_the_history_of_the_repository_it_names(
    committed, tmp_path, capsys, monkeypatch
):
    """The other surface of the same variable, and the quieter one: `sha --write` at
    least printed a new fingerprint, while `validate` under `GIT_DIR` walked the other
    repository's history, found no revision of this entry, and reported `0 failure(s)`
    over a frozen region a commit was holding. The failures are named here so that a
    scrub that reaches `sha` and not the checkers cannot pass.
    """
    project, path = committed
    monkeypatch.setenv("GIT_DIR", str(elsewhere_repository(tmp_path) / ".git"))
    drift_the_frozen_region(path)
    capsys.readouterr()
    assert project.cl("validate") == 1
    out = capsys.readouterr().out
    assert "the region above the APPEND marker is immutable" in out


def test_a_git_that_cannot_read_the_entry_at_head_is_not_a_git_saying_not_committed(
    committed, tmp_path, capsys, monkeypatch
):
    """The scrub keeps `GIT_OBJECT_DIRECTORY` out of the environment; this holds the
    second half of that repair, which is why the variable was able to do anything. The
    question `sha --write` asks went through `git()`, and `git()` answers None both for
    an entry HEAD does not have and for a git that could not look — so an object store
    git could not read the entry out of read as `not committed yet`.

    The shim fails exactly the lookup of a path at HEAD and delegates everything else, so
    the repository is otherwise intact and `git_problem()` has nothing to report: what is
    under test is the one answer. Restoring `git(...) is not None` reddens it.
    """
    project, path = committed
    shim = tmp_path / "shim-bin"
    shim.mkdir()
    real = subprocess.run(["which", "git"], capture_output=True, text=True, check=True)
    (shim / "git").write_text(
        "#!/bin/sh\n"
        'for a in "$@"; do case "$a" in HEAD:*) exit 128;; esac; done\n'
        f'exec {real.stdout.strip()} "$@"\n',
        encoding="utf-8",
    )
    (shim / "git").chmod(0o755)
    monkeypatch.setenv("PATH", f"{shim}{os.pathsep}{os.environ['PATH']}")
    before = path.read_text(encoding="utf-8")
    drift_the_frozen_region(path)
    capsys.readouterr()
    assert project.cl("sha", "--write", str(path)) == 2
    assert "could not be established" in capsys.readouterr().err
    assert path.read_text(encoding="utf-8") == before.replace(*FROZEN_EDIT)


def test_cached_reads_the_index_git_is_building_the_commit_in(committed, capsys, monkeypatch):
    """The scrub, pointed the other way, and the reason `GIT_INDEX_FILE` survives it for
    the callers whose subject is the index.

    `git commit -- <path>` commits the working tree's version of the named paths and
    HEAD's version of everything else, out of a temporary index it builds and names to
    the hook in `GIT_INDEX_FILE` — `.git/next-index-<pid>.lock`, measured on git 2.43.0.
    The index the fixture builds below is that index. `validate --cached` must read it,
    because it is the content the commit will hold; reading `.git/index` instead — which
    is what dropping `index=True` does — passes the commit that rewrites a frozen region.
    Both answers are asserted, because the test's whole content is that they differ.
    """
    project, path = committed
    drift_the_frozen_region(path)
    partial = project.root / ".git" / "next-index-fixture.lock"
    env = {**os.environ, "GIT_INDEX_FILE": str(partial)}
    for args in (["read-tree", "HEAD"], ["add", "--", str(path)]):
        subprocess.run(["git", "-C", str(project.root), *args], check=True, env=env)

    monkeypatch.delenv("GIT_INDEX_FILE", raising=False)
    capsys.readouterr()
    assert project.cl("validate", "--cached") == 0
    assert "immutable" not in capsys.readouterr().out

    monkeypatch.setenv("GIT_INDEX_FILE", str(partial))
    capsys.readouterr()
    assert project.cl("validate", "--cached") == 1
    assert "the region above the APPEND marker is immutable" in capsys.readouterr().out


def test_cached_reads_the_entries_out_of_the_index_git_names(committed, capsys, monkeypatch):
    """The same rule one layer down. `validate --cached` reads each entry from the index
    rather than from the working tree, and which index that is has to be the one the
    commit is being built in.

    The observable is chosen so that only this can produce it: an `id` that does not match
    the filename is a failure `validate` finds by parsing the entry it loaded, so it
    appears when the entry came out of the partial index and not when it came out of
    `.git/index`. Dropping `index=True` in `load_entries` reddens it — and the
    frozen-region failure alongside does not, which is why the assertion names the
    message rather than the exit code.
    """
    project, path = committed
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("id: A0001-", "id: A0009-"), encoding="utf-8")
    index = partial_index(project, path)

    monkeypatch.setenv("GIT_INDEX_FILE", str(index))
    capsys.readouterr()
    assert project.cl("validate", "--cached") == 1
    assert "does not match filename" in capsys.readouterr().out

    monkeypatch.delenv("GIT_INDEX_FILE")
    capsys.readouterr()
    project.cl("validate", "--cached")
    assert "does not match filename" not in capsys.readouterr().out


def test_cached_freshness_reads_the_artifact_out_of_the_index_git_names(
    pinned,  # noqa: F811
    capsys,
    monkeypatch,
):
    """`freshness --cached` compares a pinned ground against what is staged, and the four
    calls that read the index — the diff against the pin, the object id of the artifact,
    whether it is still there, and the section text — must all be reading the same one.
    A drift staged into the index the commit is being built in is a drift that commit
    lands; read out of `.git/index` instead it is invisible, and the hook passes it.
    """
    note = pinned.root / "docs" / "note-001.md"
    pinned.note(note.read_text(encoding="utf-8").replace("0.04", "0.09"))
    index = partial_index(pinned.p, note)

    monkeypatch.delenv("GIT_INDEX_FILE", raising=False)
    capsys.readouterr()
    pinned.p.cl("freshness", "--cached")
    assert "has moved" not in capsys.readouterr().out

    monkeypatch.setenv("GIT_INDEX_FILE", str(index))
    capsys.readouterr()
    pinned.p.cl("freshness", "--cached")
    assert "has moved" in capsys.readouterr().out


def test_an_index_git_cannot_parse_is_reported_even_when_it_is_not_the_default_one(
    committed, capsys, monkeypatch
):
    """`index_problem` is the guard that stops `--cached` falling back to the working tree
    without saying so, and it has to ask about the index git named. Pointed at
    `.git/index` while `GIT_INDEX_FILE` names something unparseable, it reports a healthy
    index and the fallback goes unmentioned — which is the surface MEDIUM-33 exists for.
    """
    project, _ = committed
    broken = project.root / ".git" / "next-index-fixture.lock"
    broken.write_bytes(b"this is not an index file")
    monkeypatch.setenv("GIT_INDEX_FILE", str(broken))
    capsys.readouterr()
    project.cl("validate", "--cached")
    assert "the git index cannot be read" in capsys.readouterr().err


def test_cached_compares_the_bytes_of_the_index_git_names(committed, capsys, monkeypatch):
    """The byte half of the frozen-region check reads the staged blob directly rather than
    the parsed entry, so it is a second reader of the index and needs the same one.

    A frozen region rewritten from LF to CRLF has the same text and none of the same
    bytes, which is why that check exists; staged into the index the commit is being built
    in, it is a rewrite that commit lands. Reading `.git/index` for those bytes — dropping
    `index=cached` from `check_history`'s batch — compares the entry against itself and
    finds nothing, and no other assertion in this file notices.
    """
    project, path = committed
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    index = partial_index(project, path)

    monkeypatch.delenv("GIT_INDEX_FILE", raising=False)
    capsys.readouterr()
    project.cl("validate", "--cached")
    assert "not the same bytes" not in capsys.readouterr().out

    monkeypatch.setenv("GIT_INDEX_FILE", str(index))
    capsys.readouterr()
    assert project.cl("validate", "--cached") == 1
    assert "not the same bytes" in capsys.readouterr().out


def test_cached_sees_a_deletion_staged_into_the_index_git_names(
    pinned,  # noqa: F811
    capsys,
    monkeypatch,
):
    """Whether the artifact is still there is asked of the index too, with
    `ls-files --error-unmatch`, and a commit that removes a ground is exactly the commit
    a hook must not wave through. Staged into the partial index the removal is a
    withdrawn ground; asked of `.git/index`, which still holds the file, it is nothing at
    all — and the two answers are the assertion.
    """
    note = pinned.root / "docs" / "note-001.md"
    note.unlink()
    index = partial_index(pinned.p, note)

    monkeypatch.delenv("GIT_INDEX_FILE", raising=False)
    capsys.readouterr()
    pinned.p.cl("freshness", "--cached")
    assert "the ground it names is gone" not in capsys.readouterr().out

    monkeypatch.setenv("GIT_INDEX_FILE", str(index))
    capsys.readouterr()
    pinned.p.cl("freshness", "--cached")
    assert "is not in the index; the ground it names is gone" in capsys.readouterr().out


def test_cached_write_records_the_artifact_as_the_named_index_has_it(
    pinned,  # noqa: F811
    monkeypatch,
):
    """`freshness --write` records the object id of the artifact it compared, and that
    record is what a later run reads to decide whether a verdict discharges the drift in
    front of it. Read out of the wrong index it records the id the pin already has, which
    is a verdict stating no drift — a forgery the machinery wrote itself.
    """
    note = pinned.root / "docs" / "note-001.md"
    pinned.note(note.read_text(encoding="utf-8").replace("0.04", "0.09"))
    index = partial_index(pinned.p, note)
    staged = pinned.p.blob("docs/note-001.md")

    monkeypatch.setenv("GIT_INDEX_FILE", str(index))
    pinned.p.cl("freshness", "--write", "--cached")
    assert f"artifact: {staged}" in pinned.entry_path().read_text(encoding="utf-8")


@pytest.fixture
def plainly_pinned(project):
    """A project whose entry rests on a whole artifact — no section — at a commit, with
    nothing edited since. The `pinned` fixture above pins a section, and a sectioned
    pointer reads the artifact's text and compares the section itself, which quietly
    corrects a wrong answer from git's `diff`. A plain pointer has nothing inside it to
    narrow to, so `diff` is the whole verdict — which is what makes this the shape that
    catches an environment reaching a call nobody thought was reading the index.
    """
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the artifact, before any claim rests on it")
    pin = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert project.cl("new", "fraction-law") == 0
    path = project.write_full_entry(next(project.entries.glob("A0001-*.md")))
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            'lab: docs/note-001.md § "Observation" @working',
            f"experiment: docs/note-001.md @{pin}",
        ),
        encoding="utf-8",
    )
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    return project


@pytest.mark.parametrize("value", ["", "no-such-index", "{other}/.git/index"])
def test_an_untouched_plain_ground_is_not_moved_under_a_foreign_index(
    plainly_pinned, tmp_path, capsys, monkeypatch, value
):
    """`GIT_INDEX_FILE` is the one variable kept out of the scrub, and it is kept for
    `--cached`. This is the call it reaches that has nothing to do with `--cached`:
    `git diff <pin> --name-only -- <path>` consults the index even when nobody asked it
    to, so under an index that does not hold the artifact — a foreign one, a path that is
    not there, the empty string — git calls an untouched file changed. A plain pointer
    takes that as the verdict, and the run flags a ground nobody edited.

    Measured on git 2.43.0: `git diff <pin> --name-only -- <path>` over an unchanged path
    prints nothing with the repository's own index and prints the path under all three
    values above. The scrub is why the ambient variable never arrives — `drift` passes
    `git_env(index=cached)`, and this run is not `--cached`.

    This is the rule that seven index-site mutants and twelve parametrized variables all
    missed: `sha --write` reads no index, so the variable cannot bite there, and every
    other freshness test in the suite pins a section, so `scoped()` re-reads the text and
    corrects git's answer before anyone sees it. Deleting `"GIT_INDEX_FILE"` from
    `GIT_REPOSITORY_ENV` — which makes `git_env(index=True)` and `git_env(index=False)`
    the same environment, and so unmakes the whole distinction this module is about —
    passed the entire suite until this test existed. (QE14-1.)
    """
    other = elsewhere_repository(tmp_path, "another-repository")
    monkeypatch.setenv("GIT_INDEX_FILE", value.format(other=other))
    capsys.readouterr()
    assert plainly_pinned.cl("freshness") == 0
    assert "has moved" not in capsys.readouterr().out


def test_an_entry_whose_blob_is_gone_is_still_a_committed_entry(committed, capsys):
    """`rev-parse --verify` and `cat-file -e` disagree where neither of them fails, and
    the disagreement is in this repair's favour. `rev-parse` resolves the name through
    the tree without checking the object is present; `cat-file -e` reads it and exits 1
    when it is not there — which `git()` folded into `not committed yet`, so `main`
    rewrote the frozen region of an entry a commit was holding.

    What makes the region immutable is that a commit names it, not whether this checkout
    can still read the bytes. Removing the loose blob is how a corrupted object store, a
    partial clone or a lost file reaches this code. (QE14-4.)
    """
    project, path = committed
    rel = path.relative_to(project.root)
    blob = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", f"HEAD:{rel}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    loose = project.root / ".git" / "objects" / blob[:2] / blob[2:]
    assert loose.is_file(), "the fixture's blob is packed; this test needs it loose"
    loose.unlink()

    before = path.read_text(encoding="utf-8")
    drift_the_frozen_region(path)
    capsys.readouterr()
    assert project.cl("sha", "--write", str(path)) == 2
    assert "is committed" in capsys.readouterr().err
    assert path.read_text(encoding="utf-8") == before.replace(*FROZEN_EDIT)
