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

from claims_ledger import freshness, resolve, schema, validate
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
    # Two cases below degrade git by deleting one loose object, which only degrades
    # anything while the object *is* loose. On the CI runners this failed twice in one
    # day, on different legs each time and never locally: `test_e` raised FileNotFoundError
    # unlinking a path for a blob `rev-parse` had just resolved, and `test_e2` unlinked
    # HEAD's commit object and watched `git log` go on answering — both of which say the
    # object was in a pack. Auto-packing is off for these repositories, so the precondition
    # holds rather than depending on which git the runner shipped.
    project.git("config", "gc.auto", "0")
    project.git("config", "maintenance.auto", "false")
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
    loose = pinned.root / ".git" / "objects" / blob[:2] / blob[2:]
    assert loose.is_file(), (
        f"precondition: {blob} is a loose object. It is not, so something packed it and "
        "deleting this file would degrade nothing — see the auto-packing config in "
        "make_pinned()"
    )
    loose.unlink()
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

    loose = pinned.root / ".git" / "objects" / head[:2] / head[2:]
    assert loose.is_file(), (
        f"precondition: {head} is a loose object. It is not, so something packed it and "
        "deleting this file would degrade nothing — see the auto-packing config in "
        "make_pinned()"
    )
    loose.unlink()
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
    1 over it, where a git that cannot look exits 128 or does not return — so that exit 1
    is git saying the pin resolves to nothing, and a pin that resolves to nothing is
    `resolve`'s subject. `freshness` stays quiet on purpose: reporting one defect under
    two names would make it look like two. What must never happen is that nobody reports
    it, and this is the test of that.
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
    rc, _, err = _git(p.root, "rev-parse", "--verify", "--quiet", "beef")
    assert rc == 1, "git's answer is `it does not resolve`, not `I cannot say`"
    # Not read from stderr: git warns there over a broken ref and says nothing over an
    # absent one, which tells two kinds of `no` apart rather than `no` from a failure.
    assert "dangling symref" in err
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


# --- GITFAIL-8: a git that cannot say whether the drift happened -----------------------


def _shim_git_that_cannot(tmp_path, subcommand):
    """A real `git` on PATH that fails one subcommand and delegates the rest.

    Everywhere else in this file the failure is produced by configuring git, which is
    better evidence. It cannot reach this one: `git log --raw` reads history and runs no
    clean filter, so there is nothing to configure that stops it and leaves
    `rev-parse --git-dir` working. The shim is still a real git failing for real — a
    non-zero exit from the binary the package invokes — and not a patched internal.
    """
    d = tmp_path / "shim-bin"
    d.mkdir(exist_ok=True)
    real = shutil.which("git")
    (d / "git").write_text(
        "#!/bin/sh\n"
        f'for a in "$@"; do [ "$a" = "{subcommand}" ] && exit 128; done\n'
        f'exec {real} "$@"\n',
        encoding="utf-8",
    )
    (d / "git").chmod(0o755)
    return d


def test_j_a_git_that_cannot_say_whether_the_drift_happened_says_so(pinned, tmp_path, monkeypatch):
    """The orphan rule's own git call, brought under this file's discipline. `orphans()`
    asks history whether the artifact really was what the verdict records; when git cannot
    answer, the check did not run, and a check that did not run is never a check that
    passed. The predecessor of this code read a failed `rev-list` as "it drifted" and
    retired the forged-discharge check in silence.
    """
    pinned.note(NOTE.replace("0.04", "0.09"))
    pinned.run(write=True)  # the discharge, recording the artifact the drift was seen at
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "remeasure, and the discharge the checker wrote")
    pinned.note(NOTE)  # undone, so the verdict is the one thing left to judge
    assert pinned.outcomes() == [], "precondition: the discharge stands"

    monkeypatch.setenv(
        "PATH", f"{_shim_git_that_cannot(tmp_path, 'log')}{os.pathsep}{os.environ['PATH']}"
    )
    got = pinned.outcomes()
    assert [o for o, _, _ in got] == ["fail"], f"the silence of a git that could not answer: {got}"
    assert "could not be established" in got[0][2]


# ---------------------------------------------------------------------------
# The one command `git_problem()` asks, broken: `git rev-parse --git-dir`.
# ---------------------------------------------------------------------------


def break_git_dir(tmp_path, monkeypatch):
    """After this, `git rev-parse --git-dir` fails in every repository -- the one
    command `git_problem()` asks -- while every other git command still runs for real.

    The two tests below arrived here with a second copy of `_shim_git_that_cannot` under
    them, written the same way against the same `exit 128`. One shim is enough.
    """
    shim = _shim_git_that_cannot(tmp_path, "--git-dir")
    monkeypatch.setenv("PATH", f"{shim}{os.pathsep}{os.environ['PATH']}")


def test_a_broken_git_is_not_settled_as_pointers_that_do_not_resolve(pinned, tmp_path, monkeypatch):
    """resolve.py's own comment: a git that could not be asked leaves pinned pointers
    "unjudged rather than blamed" -- `run()` asks `git_problem()` once, for the ledger,
    and says so in one report naming `Grounds`. Deleting that report left every pinned
    pointer silently unjudged, which is indistinguishable, at the CLI, from every one of
    them resolving cleanly."""
    break_git_dir(tmp_path, monkeypatch)
    reports = resolve.run(pinned.ledger())
    assert reports, "a git that could not answer produced no report at all"
    assert [r.outcome for r in reports] == ["fail"]
    assert reports[0].part == "Grounds"
    assert "pinned pointers were not read out of git" in reports[0].message


def test_a_broken_git_is_not_a_freshness_check_that_ran(pinned, tmp_path, monkeypatch):
    """freshness.py's docstring reserves silence for exactly the case this refuses:
    `run()` returns one `fail` report naming `freshness` and saying the check did not
    run, rather than the empty list a clean run and a check that never ran are
    otherwise identical to."""
    break_git_dir(tmp_path, monkeypatch)
    reports = pinned.run()
    assert reports, "a git that could not answer produced no report at all"
    assert [r.outcome for r in reports] == ["fail"]
    assert reports[0].part == "freshness"
    assert "freshness did not run" in reports[0].message


# ---------------------------------------------------------------------------
# The live-drift path's own two "git could not answer" branches.
# ---------------------------------------------------------------------------
#
# `drift()` reports what moved; these two are asked afterwards, about a ground that has
# already moved, and each is the moment a *different* git call fails. They are the same
# rule as everything above -- a check that did not run is never a check that passed --
# at the one surface where failing it costs the ledger its suppression rule rather than
# a diagnosis.
#
# Neither is reachable from a corpus seed: a seed is files on disk and cannot express
# "the git binary answers badly", so only a shimmed PATH can put the question.


def test_a_git_that_cannot_weigh_the_acknowledgement_does_not_silence_the_drift(
    pinned, tmp_path, monkeypatch
):
    """A drifted ground whose acknowledgement does not record what this run reads: the
    cheap half of `discharges()` cannot settle it, so `caused()` asks history. When git
    cannot answer, the verdict neither discharges the drift nor fails to.

    Silence retires the suppression rule -- the drift is live and reported as nothing.
    An accusation forges one against what may be a correct discharge. The branch exists
    to do neither.
    """
    pinned.note(NOTE.replace("0.04", "0.09"))
    pinned.run(write=True)  # the discharge, recording the artifact at this drift
    pinned.p.git("add", "-A")
    pinned.p.git("commit", "-qm", "remeasure, and the discharge the checker wrote")
    # Moved again, so the acknowledgement records an artifact that is not what this run
    # reads and the comparison falls through to history.
    pinned.note(NOTE.replace("0.04", "0.11"))
    assert pinned.outcomes() == [], (
        "precondition: with a working git the acknowledgement is weighed against history "
        "and stands, so the drift is discharged and nothing is reported"
    )

    monkeypatch.setenv(
        "PATH", f"{_shim_git_that_cannot(tmp_path, 'log')}{os.pathsep}{os.environ['PATH']}"
    )
    got = pinned.outcomes()
    assert "fail" in [o for o, _, _ in got], (
        f"the drift is live and whether the verdict discharges it could not be "
        f"established; the run reported no failure: {got}"
    )
    assert [m for _, _, m in got if "could not be established" in m], (
        f"the run failed without saying that git is what could not answer: {got}"
    )


def test_write_does_not_append_a_verdict_it_cannot_state_and_says_why(
    pinned, tmp_path, monkeypatch
):
    """`--write` records what the artifact was when the drift was seen, and `orphans()`
    holds the verdict to exactly that afterwards. A verdict this run cannot state is one
    nothing could ever check, so it is not appended -- and a `--write` that declines to
    write must not decline in silence, or the drift is left unrecorded and unreported at
    once.
    """
    pinned.note(NOTE.replace("0.04", "0.09"))
    before = pinned.entry_path().read_text(encoding="utf-8")
    monkeypatch.setenv(
        "PATH", f"{_shim_git_that_cannot(tmp_path, 'hash-object')}{os.pathsep}{os.environ['PATH']}"
    )
    got = pinned.outcomes(write=True)

    assert pinned.entry_path().read_text(encoding="utf-8") == before, (
        "precondition for the rule: git could not say what the artifact is, so no verdict "
        "is appended"
    )
    assert "fail" in [o for o, _, _ in got], (
        f"nothing was written and the run did not fail: the drift is now neither "
        f"recorded nor reported: {got}"
    )
    assert [m for _, _, m in got if "no verdict was appended" in m], (
        f"the run failed without saying that no verdict was appended, or why: {got}"
    )


# --- GITFAIL-8: a diagnosis of the pin, built on a git that failed to answer -----------
#
# `resolve` names why a pinned pointer did not resolve, because `does not resolve` alone
# said the same thing for a commit dropped by a squashed history and for a renamed path,
# whose repairs differ by a supersession per entry. A diagnosis is worth more than a
# symptom and costs more when it is wrong, so these three hold the sentence to what git
# actually established. The `qe` fix-review gate on ticket `f52f2f29823b4650` measured
# the first two as confident falsehoods before they were fixed.


def test_l_a_show_that_failed_is_not_reported_as_a_path_that_is_missing(
    pinned, tmp_path, monkeypatch
):
    """The commit is there, the path is in it, and `git show` failed anyway. `git()` folds
    `no` and `could not answer` into one None, so a diagnosis built on it stated as fact
    what it never established — and this state passes the `unasked` gate in `run()`, which
    asks `rev-parse --git-dir` and nothing more. The answer must name git, not the pointer.
    """
    monkeypatch.setenv(
        "PATH", f"{_shim_git_that_cannot(tmp_path, 'show')}{os.pathsep}{os.environ['PATH']}"
    )
    got = [(r.outcome, r.message) for r in resolve.run(pinned.ledger())]
    assert [o for o, _ in got] == ["fail"], f"the pointer must still fail: {got}"
    assert "still did not return the content" in got[0][1], (
        f"the failure blamed the pointer for a git that could not answer: {got}"
    )
    assert "is not in it" not in got[0][1], (
        f"it asserted the path is absent from a commit that has it: {got}"
    )


def test_m_a_shallow_clone_is_not_reported_as_a_rewritten_history(pinned, tmp_path):
    """A shallow clone has no object for a commit that is perfectly well upstream, which
    is the same silence a squash leaves behind. Telling a person their history was
    rewritten sends them to a supersession per entry for a repair that is `--unshallow`.
    """
    clone = tmp_path / "shallow"
    rc, _, err = _git(
        pinned.root, "clone", "-q", "--depth", "1", f"file://{pinned.root}", str(clone)
    )
    assert rc == 0, err
    assert _git(clone, "rev-parse", "--is-shallow-repository")[1].strip() == "true"
    assert _git(clone, "cat-file", "-t", pinned.pin)[0] != 0, (
        "precondition: the pinned commit is outside the graft boundary"
    )
    # The clone carries no `ledger/cache/` — it is gitignored — so the source bytes fail
    # too. The pin's own report is the subject here, selected rather than assumed alone.
    got = [(r.outcome, r.message) for r in resolve.run(open_ledger(root=clone))]
    pin = [m for o, m in got if o == "fail" and "does not resolve" in m]
    assert len(pin) == 1, f"the pointer must still fail, exactly once: {got}"
    assert "shallow clone" in pin[0], f"the shallow clone was read as a rewrite: {pin}"
    assert "squashed" not in pin[0], f"it named a rewrite that did not happen: {pin}"


def test_n_a_pin_that_is_a_blob_is_not_reported_as_a_commit_that_is_gone(project):
    """The object is right there; it is simply not a commit. `rev-parse <pin>^{commit}`
    fails for it exactly as it fails for an object that is absent, so a diagnosis that
    asks only that question calls a mistyped pin a rewritten history.
    """
    # Hashed rather than read back out of a commit, so that `make_pinned` still makes the
    # repository's first commit itself and the object is one git really has.
    blob = subprocess.run(
        ["git", "hash-object", str(project.root / "docs" / "note-001.md")],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    p = make_pinned(project, pin_text=blob)
    got = [(r.outcome, r.message) for r in resolve.run(p.ledger())]
    assert [o for o, _ in got] == ["fail"], f"the pointer must still fail: {got}"
    assert "is a blob, not a commit" in got[0][1], f"a blob pin was misdiagnosed: {got}"
