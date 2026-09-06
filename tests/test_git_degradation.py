"""Fourth pass, dimension `gitfail`: a git that stops answering, read as good news.

The third pass established the class (HIGH-16): `schema.git()` returns None for every
failure — non-zero exit, timeout, OSError — and its callers read None as a benign
negative answer. The fix added `git_problem(repo)`, asked *once* per command, so
`skipped_checks()` could name a git that cannot answer at all.

These cases are the ones that fix does not reach. Every repository here is real and
every git failure is produced by configuring git, not by patching it: a required clean
filter whose command exits non-zero (or sleeps), a truncated `.git/index`, one loose
object removed, a dangling symref. In each, `git rev-parse --git-dir` still succeeds — so
`git_problem()` says "git is fine" — and the *next* git command fails, is read as an
answer, and a check that never ran is reported as a check that passed.

(Note for whoever fixes this: `freshness.py` does `from .schema import git`, so patching
`claims_ledger.schema.git` does not reach it. Nothing here patches git at all.)
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime

import pytest

from claims_ledger import freshness, schema, validate
from claims_ledger.config import default_config
from claims_ledger.schema import open_ledger, parse_pointer

NOTE = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.
"""


def _git(root, *args):
    """git, run for the test's own purposes; (returncode, stdout, stderr)."""
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return r.returncode, r.stdout, r.stderr


def _pointer(pin):
    return parse_pointer(f'lab: docs/note-001.md § "Observation" @{pin}')


def _head(project, short=True):
    args = ["rev-parse", *(["--short"] if short else []), "HEAD"]
    out = subprocess.run(
        ["git", "-C", str(project.root), *args], capture_output=True, text=True, check=True
    )
    return out.stdout.strip()


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
        path = self.entry_path()
        text = path.read_text(encoding="utf-8")
        head, marker, tail = text.partition("\n## References")
        path.write_text(head.rstrip("\n") + "\n\n" + block + marker + tail, encoding="utf-8")

    def outcomes(self, write=False):
        return [(r.outcome, r.part, r.message) for r in self.run(write=write)]

    def break_diff(self, command="false"):
        """Make `git diff` fail for the pinned path and nothing else: a clean filter git
        is required to run on the working-tree side of the comparison, whose command
        exits non-zero (or, with `sleep N`, outlives the per-call timeout).

        `git rev-parse --git-dir` is untouched by it, so `git_problem()` still says the
        repository is fine.
        """
        (self.root / ".gitattributes").write_text(
            "docs/note-001.md filter=boom\n", encoding="utf-8"
        )
        self.p.git("config", "filter.boom.clean", command)
        self.p.git("config", "filter.boom.smudge", "cat")
        self.p.git("config", "filter.boom.required", "true")
        assert _git(self.root, "rev-parse", "--git-dir")[0] == 0, "git_problem() must still pass"


def make_pinned(project, pin_text=None):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "the artifact, before any claim rests on it")
    pin = pin_text or _head(project)
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


@pytest.fixture
def pinned(project):
    return make_pinned(project)


# --- GITFAIL-1: a diff git refused to make is read as "unchanged" ----------------------


def test_a_diff_git_refused_to_make_is_not_a_fresh_ground(pinned):
    """Fixed: `drift()` read the None from a failed `git diff` as `unchanged`, and a
    ground that had moved was reported as `0 failure(s), 0 flag(s)`. The comparison it
    could not make is now a finding of its own."""
    pinned.note(NOTE.replace("0.04", "0.09"))
    assert pinned.outcomes(), "precondition: the ground has moved and is reported"
    pinned.break_diff()
    assert _git(pinned.root, "diff", "--name-only", pinned.pin, "--", "docs/note-001.md")[0] != 0
    assert pinned.outcomes(), (
        "the comparison did not happen; a freshness run that could not compare the pin "
        "against the working tree must not report the ground as fresh"
    )


def test_b_a_diff_that_outlived_the_timeout_is_not_a_fresh_ground(pinned, monkeypatch):
    """Fixed: GIT_TIMEOUT is per call, so a `git diff` can run out of time long after
    `git_problem()` has passed. Timing out is not an answer either."""
    monkeypatch.setattr(schema, "GIT_TIMEOUT", 2)  # the constant, not the function
    pinned.note(NOTE.replace("0.04", "0.09"))
    assert pinned.outcomes(), "precondition: the ground has moved and is reported"
    pinned.break_diff(command="sleep 30")
    assert pinned.outcomes(), (
        "the diff timed out; a freshness run that ran out of time must not report the "
        "ground as fresh"
    )


def test_c_the_cli_does_not_print_zero_flags_over_a_comparison_git_refused(pinned, capsys):
    """Fixed: the same defect at the surface a person actually reads."""
    pinned.note(NOTE.replace("0.04", "0.09"))
    pinned.break_diff()
    code = pinned.p.cl("freshness")
    out = capsys.readouterr()
    assert not (code == 0 and "0 failure(s), 0 flag(s)" in out.out and not out.err), (
        f"exit {code} with {out.out.strip()!r} on stdout and {out.err.strip()!r} on stderr"
    )


# --- GITFAIL-2: --cached silently falls back to the working tree -----------------------


def test_d_cached_says_so_when_the_index_cannot_be_read(pinned, capsys):
    """Fixed: `load_entries(cached=True)` read a failed `git show :<path>` as `not
    staged` and silently checked the working tree, so `validate --cached` — the installed
    pre-commit hook — reported on something other than what was being committed. The index
    is asked about once now, by `index_problem()`, and the fallback is named."""
    path = pinned.entry_path()
    good = path.read_text(encoding="utf-8")
    # Stage an entry whose frozen region has been edited: `--cached` must catch it.
    path.write_text(
        good.replace("mean aggregation, one layer", "mean aggregation, two layers"),
        encoding="utf-8",
    )
    pinned.p.git("add", "-A")
    path.write_text(good, encoding="utf-8")  # the working tree is clean again
    assert pinned.p.cl("validate", "--cached") == 1, "precondition: the staged entry fails"
    capsys.readouterr()

    (pinned.root / ".git" / "index").write_bytes(b"not an index" * 20)
    assert _git(pinned.root, "rev-parse", "--git-dir")[0] == 0, "git_problem() must still pass"
    rel = os.path.relpath(path, pinned.root)
    assert _git(pinned.root, "show", f":{rel}")[0] != 0, "the index is unreadable"

    code = pinned.p.cl("validate", "--cached")
    err = capsys.readouterr().err
    assert "index" in err or "--cached" in err, (
        f"exit {code} and nothing on stderr: the index could not be read and the run "
        "reported on the working tree without saying so"
    )


# --- GITFAIL-3: the append-only check skips a revision git cannot read -----------------


def _verdict(note):
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    return (
        f"- {stamp} · corroborated · grade: measured · author: main\n"
        '  evidence: lab: docs/note-001.md § "Observation" @working\n'
        f"  note: {note}\n"
    )


def test_e_append_only_is_not_waived_by_a_blob_git_cannot_read(pinned):
    """Fixed: `check_history()` skipped any consecutive pair whose blob it could not
    read, so removing one loose object retired the append-only finding it carried."""
    path = pinned.entry_path()
    pinned.append(_verdict("a second look at the same note"))
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "the verdict")
    tampered_from = _head(pinned.p, short=False)

    path.write_text(
        path.read_text(encoding="utf-8").replace("a second look", "a third look"),
        encoding="utf-8",
    )
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "the verdict, rewritten")

    def append_only_failures():
        return [r for r in validate.run(pinned.ledger()) if "append and only append" in r.message]

    assert append_only_failures(), "precondition: the rewritten verdict is caught"

    rel = os.path.relpath(path, pinned.root)
    blob = _git(pinned.root, "rev-parse", f"{tampered_from}:{rel}")[1].strip()
    (pinned.root / ".git" / "objects" / blob[:2] / blob[2:]).unlink()
    assert _git(pinned.root, "rev-parse", "--git-dir")[0] == 0, "git_problem() must still pass"
    assert _git(pinned.root, "show", f"{tampered_from}:{rel}")[0] != 0

    assert append_only_failures(), (
        "the revision the verdict was rewritten from cannot be read; the append-only "
        "check did not run and must not be reported as one that passed"
    )


# --- GITFAIL-3b: the history the immutability checks are made against ------------------


def test_e2_an_entry_whose_history_git_cannot_read_is_not_read_as_uncommitted(pinned):
    """The same class one surface further in: `check_history()` asked `git log` for an
    entry's revisions and read a failed one as an empty list, which it takes for `not yet
    committed: nothing to be immutable against`. A repository with no commits in it at
    all fails the same command the same way, and is the ordinary state of a ledger being
    scaffolded, so the two are separated rather than collapsed."""
    path = pinned.entry_path()
    rel = os.path.relpath(path, pinned.root)
    head = _head(pinned.p, short=False)
    assert [r for r in validate.run(pinned.ledger()) if "history" in r.message] == [], (
        "precondition: the history reads"
    )

    (pinned.root / ".git" / "objects" / head[:2] / head[2:]).unlink()
    assert _git(pinned.root, "rev-parse", "--git-dir")[0] == 0, "git_problem() must still pass"
    assert _git(pinned.root, "rev-parse", "--verify", "--quiet", "HEAD")[0] == 0
    assert _git(pinned.root, "log", "--format=%H", "--", rel)[0] != 0

    assert [r for r in validate.run(pinned.ledger()) if "cannot read the history" in r.message], (
        "the revisions the frozen region is compared against could not be listed; that is "
        "not an entry that has never been committed"
    )


# --- GITFAIL-4: a pin git could not classify -------------------------------------------


def test_f_a_pin_git_could_not_classify_is_not_taken_for_a_commit(tmp_path):
    """Fixed: `is_object_name()` read a failed `rev-parse --symbolic-full-name` as `not a
    ref` and accepted the pin as an object name, so a git that could not answer retired
    the unstable-pin flag without a word. It answers None now for a git that could not be
    asked, and `drift` turns that into a finding rather than into silence."""
    outside = tmp_path / "not-a-repository"
    outside.mkdir()
    assert _git(outside, "rev-parse", "--symbolic-full-name", "beef")[0] != 0
    assert freshness.is_object_name(outside, "beef")[0] is None
    assert (
        freshness.drift(outside, _pointer("beef"), outside, default_config(outside))[0] == "unknown"
    )


def test_f2_a_dangling_symref_pin_is_reported_where_the_pin_is_the_subject(project, capsys):
    """The configuration GITFAIL-4 was reported on, and what it actually is.

    A dangling symref is not a git that cannot answer. `rev-parse --verify --quiet` exits
    1 over it with nothing on stderr, which is git saying the pin resolves to nothing —
    and a pin that resolves to nothing is `resolve`'s subject. `freshness` stays quiet on
    purpose: reporting one defect under two names would make it look like two. What must
    never happen is that nobody reports it, and this is the test of that.
    """
    p = make_pinned(project, pin_text="beef")
    p.p.git("branch", "beef")
    assert [o for o, _, m in p.outcomes() if "pinned to a name" in m], (
        "precondition: `beef` is a branch and the pin is flagged as unstable"
    )
    # A dangling symref: the branch is still there, and git can no longer say what it is.
    (p.root / ".git" / "refs" / "heads" / "beef").write_text("ref: refs/heads/gone\n")
    assert _git(p.root, "rev-parse", "--git-dir")[0] == 0, "git_problem() must still pass"
    assert _git(p.root, "rev-parse", "--symbolic-full-name", "beef")[0] != 0
    assert _git(p.root, "rev-parse", "--verify", "--quiet", "beef")[0] == 1, (
        "git's answer is `it does not resolve`, not `I cannot say`"
    )
    capsys.readouterr()
    assert p.p.cl("check") == 1
    assert "@beef does not resolve" in capsys.readouterr().out


# --- GITFAIL-5: a failed diff forges an orphan -----------------------------------------


def test_g_a_failed_diff_does_not_forge_an_orphan(pinned):
    """Fixed: `orphans()` read the (None, None) of a failed diff as `that ground has not
    drifted` and failed a correctly discharged verdict. The accusation needs the drift to
    be established, and a comparison that did not happen establishes nothing."""
    pinned.note(NOTE.replace("0.04", "0.09"))
    pinned.run(write=True)  # appends the contested verdict that discharges the drift
    assert pinned.outcomes() == [], "precondition: the drift is discharged"
    pinned.break_diff()
    assert not [m for _, _, m in pinned.outcomes() if "orphan" in m], (
        "the ground still drifted; a git that cannot make the diff must not turn its "
        "silence into a verdict nothing caused"
    )


# --- GITFAIL-6: `sha --write` never asks whether git can answer ------------------------


def test_h_sha_write_does_not_rewrite_a_committed_entry_when_git_cannot_say(
    pinned, monkeypatch, capsys
):
    """Fixed: `is_committed()` read a failed `git cat-file -e HEAD:<path>` as `not
    committed`, so with no git on PATH `sha --write` rewrote the immutable frozen region
    of a committed entry, exited 0 and said nothing."""
    path = pinned.entry_path()
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "mean aggregation, one layer", "mean aggregation, two layers"
        ),
        encoding="utf-8",
    )
    before = path.read_text(encoding="utf-8")
    assert pinned.p.cl("sha", "--write", str(path)) == 2, (
        "precondition: with git, rewriting a committed entry's fingerprint is refused"
    )
    capsys.readouterr()

    nowhere = pinned.root / "nogit"
    nowhere.mkdir()
    monkeypatch.setenv("PATH", str(nowhere))
    assert shutil.which("git") is None
    code = pinned.p.cl("sha", "--write", str(path))
    err = capsys.readouterr().err
    assert path.read_text(encoding="utf-8") == before or err, (
        f"exit {code}: the frozen region of a committed entry was rewritten by a run "
        "that had no way to find out that it was committed, and nothing was said"
    )


# --- GITFAIL-7: the diagnosis blames the pointer for git's absence ---------------------


def test_i_a_missing_git_is_not_a_pointer_that_does_not_resolve(pinned, monkeypatch, capsys):
    """Fixed: with no git to ask, every pinned pointer came back None and was reported as
    one that does not resolve — a diagnosis of the pointer for a question nobody put."""
    nowhere = pinned.root / "nogit"
    nowhere.mkdir()
    monkeypatch.setenv("PATH", str(nowhere))
    assert shutil.which("git") is None
    pinned.p.cl("resolve")
    out = capsys.readouterr()
    assert "does not resolve" not in out.out, (
        "git was never on PATH to be asked; the pin is not the thing that failed\n"
        f"stdout: {out.out}\nstderr: {out.err}"
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pytest.main([__file__, "-q"]))
