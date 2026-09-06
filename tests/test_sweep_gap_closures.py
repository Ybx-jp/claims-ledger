"""Sixth pass, HIGH-59: four report sites an independent AST sweep found held by
neither the red-team corpus nor the unit suite.

The sweep (`.qe/probe6/enumerate_sites.py`) found 116 report sites at the tip it ran
against, of which 50 survived both the corpus and the full unit suite. Seven of the
fifty are not well-formedness guards -- they are the "not silently passing" class
`corpus/README.md` names outright. Three of the seven now have a corpus seed:
D05-dead-pointer gained an `entry:` ground that names an id the ledger does not have
(caught by both `resolve` and `references`) and a `search:` ground whose `query=` is
empty (caught by `resolve`). The other four cannot be reached through a seed by
construction, because what breaks each of them is not a seed's *content*:

- `resolve.run()`'s and `freshness.run()`'s own `git_problem()` branches fire only when
  git is on PATH and answers, but answers badly, for the one command each asks. A seed
  is files on disk; it cannot express "the git binary itself is broken," only a shimmed
  PATH can, and the corpus runner has no channel for one.
- `references.run()`'s own `read_document()` re-check exists for the reason `resolve`
  and `freshness` distinguish "could not answer" from "answered no" everywhere else:
  `schema.tree_documents()` (and the corpus runner's own reimplementation of it, in
  `corpus/run.py`'s `seed_ledger()`) both filter unreadable documents once, before any
  checker runs -- so `ledger.docs` can never itself hold a path that was unreadable at
  that moment, and no seed's static files can stage otherwise. The re-check only fires
  when a document that *was* readable when the ledger was built stops being readable
  before the checker gets to it: a race between two reads of the same path, not a
  property of what the path contains.
- `propagate.run()`'s `--write` flag report is unreachable from the corpus by
  construction, per `corpus/README.md`: the runner binds every checker read-only
  (`write=False`), so `propagate --write` never runs inside it at all.

Each test below asserts on the report's own message and outcome, not only on an exit
code. `test_invariants.py`'s `propagate --write` fixed-point tests already prove the
write converges; they pass unchanged with the flag report deleted, because the run's
pre-existing `fail` report (the missing verdict, present whether or not `--write` fixes
it) forces the same non-zero exit either way. That is exactly the gap this file closes.
"""

from __future__ import annotations

import os
import subprocess

from conftest import QUOTE
from test_git_degradation import pinned  # noqa: F401 -- the fixture, reused as-is
from test_invariants import append_verdict_text, fill_entry, set_stated

from claims_ledger import propagate, references, resolve
from claims_ledger.schema import open_ledger


def shim_git(tmp_path, failing_arg):
    """A `git` on PATH that fails whenever `failing_arg` appears among its arguments and
    delegates everything else to the real one -- the same shape of failure
    test_git_degradation.py and test_pass6_regressions.py both use, so a repository this
    git cannot fully answer is produced by configuring git, not by patching it."""
    d = tmp_path / "shim-bin"
    d.mkdir(exist_ok=True)
    real = subprocess.run(["which", "git"], capture_output=True, text=True, check=True)
    (d / "git").write_text(
        "#!/bin/sh\n"
        f'for a in "$@"; do [ "$a" = "{failing_arg}" ] && exit 128; done\n'
        f'exec {real.stdout.strip()} "$@"\n',
        encoding="utf-8",
    )
    (d / "git").chmod(0o755)
    return d


def break_git_dir(tmp_path, monkeypatch):
    """After this, `git rev-parse --git-dir` fails in every repository -- the one
    command `git_problem()` asks -- while every other git command still runs for real."""
    shim = shim_git(tmp_path, "--git-dir")
    monkeypatch.setenv("PATH", f"{shim}{os.pathsep}{os.environ['PATH']}")


# === resolve.py: a broken git is not settled as pointers that do not resolve ===========


def test_a_broken_git_is_not_settled_as_pointers_that_do_not_resolve(pinned, tmp_path, monkeypatch):  # noqa: F811
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


# === freshness.py: the same branch, on the checker whose whole subject is git history ==


def test_a_broken_git_is_not_a_freshness_check_that_ran(pinned, tmp_path, monkeypatch):  # noqa: F811
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


# === references.py: its own re-check of a document the ledger already listed ===========


def test_a_document_unreadable_only_after_the_ledger_listed_it_is_not_silent(project):
    """references.py's comment: "A document that could not be opened at all, and one
    that fails at the read: either way its citations were not checked." The first half
    is `ledger.unreadable_docs`, seeded by D50; this is the second half, which fires only
    when a document that passed the ledger's own listing stops being readable before the
    checker gets to it -- the race `tree_documents()`'s one-time filter cannot itself
    prevent."""
    doc = project.root / "docs" / "cites-nothing-special.md"
    doc.write_text("An ordinary document, citing nothing in particular.\n", encoding="utf-8")
    ledger = open_ledger(root=project.root)
    assert any(name == "docs/cites-nothing-special.md" for name, _ in ledger.docs), (
        "the document must be listed as readable for the re-check below to mean anything"
    )
    doc.unlink()  # the race: gone between the listing above and references.run() below
    reports = references.run(ledger)
    assert any(
        r.part == "docs/cites-nothing-special.md" and "its citations were not checked" in r.message
        for r in reports
    ), reports


# === propagate.py: the --write flag names what it appended =============================


def test_the_write_flag_names_what_propagate_appended(project):
    """propagate.py's module docstring: "--write appends the missing verdicts ... the
    run still exits non-zero so the change is looked at before it is committed." The
    exit-code half of that promise is already proven by
    test_invariants.py's fixed-point tests; this proves the other half, that the report
    a person is meant to look at actually names what was appended and by whom."""
    project.cl("new", "base-claim")
    base = project.write_full_entry(project.entry("A0001-base-claim.md"))
    set_stated(base, "2020-01-01T00:00:00+00:00")
    append_verdict_text(
        base,
        timestamp="2020-02-01T00:00:00+00:00",
        status="refuted",
        grade="measured",
        author="main",
        evidence="source: fx-source · whole text",
        note="a later sweep contradicts it",
    )

    project.cl("new", "dependent-claim")
    dep = project.entry("A0002-dependent-claim.md")
    fill_entry(
        project,
        dep,
        assertion="A dependent claim that rests in part on the base claim.",
        grounds=(
            '- lab: docs/note-001.md § "Observation" @working\n'
            "- source: fx-source · whole text\n"
            "- entry: A0001-base-claim · cites-as-live"
        ),
        warrant="The base claim, if it holds, supports this one under the same regime.",
        backing=f'- source: fx-source · whole text\n  speaker: Okafor\n  quote: "{QUOTE}"',
    )

    reports = propagate.run(open_ledger(root=project.root), write=True)
    flags = [r for r in reports if r.outcome == "flag"]
    assert flags, "propagate --write appended a verdict and reported nothing about it"
    assert any(
        "appended" in r.message
        and "contested verdict" in r.message
        and "by propagation" in r.message
        for r in flags
    ), flags
