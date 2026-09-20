"""The `claims-ledger` command.

Five checkers, an authoring side, the neighbours lookup, and the corpus that proves the
checkers. What every checking subcommand exits with is decided in one place,
`report_command`, which is where the rule is stated.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import difflib
import os
import shlex
import statistics
import sys
import tempfile
from pathlib import Path

from . import (
    __version__,
    authoring,
    freshness,
    harness,
    lift,
    neighbours,
    propagate,
    references,
    renumber,
    resolve,
    validate,
)
from .authoring import AuthoringError, refuse_to_write_outside_the_root
from .config import ConfigError, leaves_root
from .schema import (
    LedgerError,
    by_id,
    entries_dir_listing_error,
    entries_for,
    exit_code,
    file_problem,
    git_available,
    git_call,
    git_problem,
    index_problem,
    index_reach,
    list_entry_files,
    load_entries,
    load_registry,
    open_ledger,
    print_reports,
    source_bytes,
    write_text_atomically,
)

CHECKERS = ("validate", "resolve", "references", "propagate", "freshness")

HOOK_TEMPLATE = """#!/bin/sh
# Installed by `claims-ledger hook --install`.
# The ledger's rules, held before the commit that would break them.
#
# The interpreter is named absolutely rather than as `claims-ledger`, because git runs
# hooks with its own environment: a console script in a virtualenv that is not active
# is not on PATH, and the hook would fail with `claims-ledger: not found` on every
# commit. `-m claims_ledger` needs nothing on PATH at all.
#
# `validate` has read `--cached` since MEDIUM-33, and the freshness line below now asks
# for it too, so that every checker here that CAN read what is actually being committed —
# the index — does, rather than whatever the working tree happens to hold when `git commit`
# runs. Left bare, a drift that is staged and then undone in the working tree before the
# hook fires committed silently: `validate --cached` saw the stale pointer, but a bare
# `freshness` looked past it at the already-reverted working tree and found nothing
# wrong. This was the surface MEDIUM-33's own writeup named as the one that matters.
#
# `resolve` asks for it too, because a ground anchored by value is held to the text the
# tree this run reads: an author who stages an artifact in one state and leaves the working
# tree in another otherwise commits an entry whose anchor no version of the path holds —
# the anchor matched the tree, and the commit carried the index.
#
# `references` and `propagate` ask for it too, and all five lines now carry it. For
# `references` that means the documents as well as the entries: a citation staged against
# one status and corrected in the tree alone otherwise passed here, because the checker
# read prose no commit contains.
#
# A ground pinned at `working` is read from the index here too: `working` names the tree
# the run reads, and under this flag that is the index. A path the index does not hold
# falls back to the working tree, which is the case the pin exists for. `freshness` passes
# such grounds over, and that is not a gap in this list — a ground with no pin has nothing
# to have moved from, and what can be asked of it, that its section is still there, is
# asked above.
set -e

# Everything below runs inside a shell function, and that is not a style choice. This
# template is a Python string in a file whose sections are top-level definitions and
# assignments, and the pattern that ends a section matches any line at column 0 carrying
# an equals sign. A shell variable assigned at the left margin therefore reads as the
# start of the next section and cuts this one short, leaving the entries pinned here
# resting on the comment above the script rather than on the script. Keep new shell
# indented inside the function, and keep an equals sign out of the first column.
run_the_checkers() {{
  # The interpreter this hook was installed with, and then the one the checkout being
  # committed to resolves, when that checkout has one of its own.
  #
  # git serves ONE hooks directory to every linked worktree — measured on git 2.43.0,
  # `rev-parse --git-path hooks` answers with the common directory from every one of them —
  # so this file is a per-repository singleton while the tree above it is per-checkout. In
  # a project that installs this package from outside its own tree those come to the same
  # thing and the recorded path is right everywhere. In a project whose tree IS the
  # package, each worktree has an editable install of its own, and the recorded path then
  # runs one checkout's package against another checkout's tree: the checkers that fire
  # are not the ones being edited, and the tree that is wrong is not the tree they read.
  #
  # So the checkout is asked first and the recorded path is the fallback. `--show-toplevel`
  # names the checkout git is committing in, which under a hook is the worktree that fired
  # it. The probe is an import rather than the file merely being there, because a
  # virtualenv without this package installed would otherwise take the hook down on every
  # commit.
  python={python}
  top=$(git rev-parse --show-toplevel 2>/dev/null) || top=""
  if [ -n "$top" ]; then
    for candidate in "$top/.venv/bin/python" "$top/venv/bin/python"; do
      [ -x "$candidate" ] || continue
      if "$candidate" -c 'import claims_ledger' >/dev/null 2>&1; then python="$candidate"; break; fi
    done
  fi

  "$python" -m claims_ledger validate --cached
  "$python" -m claims_ledger resolve --cached
  "$python" -m claims_ledger references --cached
  "$python" -m claims_ledger propagate --cached
  "$python" -m claims_ledger freshness --cached
}}

run_the_checkers
"""
# The interpreter is named absolutely and reached with `-m`, never as the `claims-ledger`
# console script (L0001-hook-names-the-interpreter-absolutely, cites-as-live) — both the
# path recorded at install time and the one the hook discovers are absolute, and the
# discovery is what makes one shared hook correct in every checkout of a repository that
# has several. git serves one hooks directory to all of them, so the recorded path would
# otherwise run one checkout's package against another checkout's tree
# (L0245-the-hook-runs-the-package-the-checkout-it-guards-resolves, cites-as-live). The hook
# asks each checker for the index wherever that checker has a `--cached` of its own. What
# each of those checkers then does with it is that checker's own claim; the template says
# only which lines carry the flag, and the lines that do not say so beside them
# (L0217-the-hook-carries-the-cached-flag-on-every-line-that-takes-one, cites-as-live).


HOOK_MARKER = HOOK_TEMPLATE.splitlines()[1]
# The template's own second line, taken from it rather than written out again, so a hook
# this package wrote is recognised by a string that cannot drift from what it writes.


def is_our_hook(path):
    """Whether what is at `path` is a pre-commit hook this package wrote.

    The marker line, not the whole text: `{python}` is interpolated at install time, so
    two installs of the same version differ wherever the interpreter does. Anything that
    cannot be read — a dangling link, a directory, bytes that are not UTF-8 — is not ours,
    which is the answer that asks the reader to decide rather than the one that offers to
    overwrite.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            head = fh.read(len(HOOK_MARKER) + 512)
    except (OSError, UnicodeDecodeError):
        return False
    return HOOK_MARKER in head.splitlines()[:4]


def hook_text(python=None):
    return HOOK_TEMPLATE.format(python=shlex.quote(python or sys.executable))


CODE_RECIPE = (
    r"'^(?:@[^\n]*\n)*(?![ \t])"
    r"(?:(?:async[ \t]+)?(?:def|class)[ \t]+{name}\b|{name}[ \t]*(?::[^=\n]+)?=)'"
)
# The `code` pattern `init` writes out commented, and the one README.md,
# docs/OPERATING.md and the `tagging-prose-with-claims` skill document; a test holds
# the four identical. It is a value substituted into the template rather than a line
# inside it because a backslash in that template is a Python escape before it is ever
# a regex one, and the recipe is mostly backslashes. Written below the assignment so
# the comment belongs to this name rather than to the section above it.


CONFIG_TEMPLATE = """# The claims ledger's layout and this project's local vocabulary.
# Every path is relative to the directory holding this file.
[tool.claims-ledger]
ledger = "{ledger}"
# entries = "entries"
# registry = "sources.jsonl"
# cache = "cache"

# Documents that may cite an entry, as globs from the project root. A citation reads
# `(A0001-<slug>, cites-as-live)` and is held to the entry's current status at every check.
# `document-excludes` is matched the same way, segment by segment: `*` stops at a
# separator, `**` spans any number of them.
documents = ["*.md", "docs/*.md"]
# document-excludes = []                    # e.g. ["docs/draft-*.md"]

# The named artifacts an entry may rest on. A `sectioned` type is written
# `lab: <path> § "<section>" @<commit>`; a plain one `experiment: <path> @<commit>`.
# The pin is what `freshness` compares against the working tree, so a pin that names a
# commit goes stale visibly and one that names a branch never can. `@working` opts out.
evidence-sectioned = ["lab"]
evidence-plain = ["experiment"]

# How a sectioned type finds its section: a regex with a `{{name}}` slot, defaulting to a
# Markdown heading. A section runs from its own header to the next one, so anchor the
# pattern at the granularity the section really has. A pattern that can nest says so with
# a group named `depth`: a match whose `depth` is longer than the header's is a
# subsection of it, not the start of the next one.
# [tool.claims-ledger.section-patterns]
# code = {code}

# Who may write a verdict, and which of those names the machinery writes under.
verdict-authors = ["main", "propagation"]
propagation-author = "propagation"

# The hand-maintained view of open hypotheses, checked against the entries.
roster = "ROSTER.md"

# Id series quarantined by an earlier ledger, which no document may cite.
archived-prefixes = []
"""

CACHE_IGNORE = """# Source bytes, keyed by sha256. The registry row is committed and
# the bytes are not: they are regenerated from the row's url and extraction method.
*
!.gitignore
"""


def build_parser():
    p = argparse.ArgumentParser(
        prog="claims-ledger",
        description="A claims ledger and the five checkers that hold it to its schema.",
    )
    p.add_argument("--version", action="version", version=f"claims-ledger {__version__}")
    p.add_argument("--root", help="project root; default is the configuration file's directory")
    p.add_argument("--config", help="configuration file to use instead of searching for one")
    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("validate", help="entries are well-formed, and history is immutable")
    v.add_argument("--cached", action="store_true", help="read staged entries from the git index")

    r = sub.add_parser("resolve", help="pointers resolve and quotations are spans of their sources")
    r.add_argument("--cached", action="store_true", help="read staged entries from the git index")
    rf = sub.add_parser("references", help="citation acts agree with statuses, both directions")
    rf.add_argument(
        "--cached", action="store_true", help="read staged entries and documents from the git index"
    )

    pr = sub.add_parser("propagate", help="dependents of fallen entries carry the contested flag")
    pr.add_argument("--write", action="store_true", help="append the missing verdicts")
    pr.add_argument("--cached", action="store_true", help="read staged entries from the git index")

    fr = sub.add_parser(
        "freshness", help="pinned grounds still name the artifact they were established on"
    )
    fr.add_argument("--write", action="store_true", help="append the missing verdicts")
    fr.add_argument(
        "--cached", action="store_true", help="compare the index rather than the working tree"
    )

    c = sub.add_parser("check", help="run all five checkers")
    c.add_argument("--cached", action="store_true", help="read staged entries from the git index")

    sub.add_parser("status", help="every entry with its kind, grade and derived status")

    nb = sub.add_parser(
        "neighbours",
        help="entries already about the same span or a nesting cohort; advisory, never a gate",
    )
    nb.add_argument(
        "target",
        nargs="?",
        help="an entry id, a path to an entry, or a ground pointer written as it would be "
        "written in an entry",
    )
    nb.add_argument(
        "--count",
        action="store_true",
        help="how many neighbours every entry has, instead of one entry's",
    )

    n = sub.add_parser(
        "new",
        help="scaffold an entry",
        # The URL goes in the epilog, which argparse prints as written: in the help text
        # of an option it was wrapped mid-token at the terminal width, and a link that
        # cannot be copied is not a link.
        epilog="The grades, and what each one requires:\n"
        "https://github.com/Ybx-jp/claims-ledger/blob/main/docs/SCHEMA.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    n.add_argument("slug", help="lowercase-and-hyphens slug; the id is allocated for you")
    n.add_argument("--id", dest="ident", help="use this id instead of the next free one")
    n.add_argument(
        "--kind",
        default="claim",
        choices=("claim", "prediction", "hypothesis"),
        help="what the entry is: a claim about what is, a prediction, or an open hypothesis",
    )
    n.add_argument(
        "--grade",
        default="measured",
        choices=("asserted", "argued", "measured", "controlled", "preregistered"),
        help="the strength of the grounds, from asserted (none) to preregistered; "
        "measured and above require a lab or experiment ground",
    )
    n.add_argument("--author", default="main", help="who states it; a lowercase author name")
    n.add_argument("--supersedes", default="none", help="the id this entry replaces, or `none`")
    n.add_argument("--credence", type=float, help="0-1; predictions carry one")
    n.add_argument("--resolves-when", help="the observation that would settle a prediction")

    r = sub.add_parser(
        "renumber",
        help="rewrite an unmerged branch so the ids it mints do not collide with another",
        description="The receiving side keeps its ids, so the branch that has not merged "
        "yet is the one that moves. Every commit on it is replaced with one that carries "
        "the new ids, so each entry is created with the id it will keep and nothing is "
        "renamed after it is committed.",
    )
    r.add_argument("--onto", default="main", help="the branch this one would merge into")
    r.add_argument("--branch", default="HEAD", help="the branch to rewrite")
    r.add_argument("--write", action="store_true", help="carry out the rewrite and move the branch")
    r.add_argument("--force", action="store_true", help="rewrite even though something was refused")
    r.add_argument(
        "--on-merge",
        action="store_true",
        help="ask as a merge guard does, and do what `merge-renumber` configures",
    )

    lifter = sub.add_parser(
        "lift", help="move a section's narrative prose onto the entry that rests on it"
    )
    lifter.add_argument("entry", help="the entry id the prose belongs to")
    lifter.add_argument(
        "--ground",
        type=int,
        help="which sectioned ground to lift from, when there is more than one",
    )
    lifter.add_argument(
        "--write", action="store_true", help="take the prose; without it, say what would be taken"
    )
    lifter.add_argument("--patch", help="write a reverse patch here, to put the prose back")
    lifter.add_argument("--author", default="main", help="the author of the passage block")
    shower = sub.add_parser("show", help="print the prose an entry holds")
    shower.add_argument("entry", help="the entry id")
    s = sub.add_parser(
        "sha", help="the verbatim fingerprint of an entry, recomputed from Scope and Backing"
    )
    s.add_argument("path", nargs="+")
    s.add_argument(
        "--write",
        action="store_true",
        help="rewrite the declared value, and fill each `=?` anchor with the digest of its "
        "section as the tree has it",
    )
    s.add_argument(
        "--force", action="store_true", help="rewrite even though git already has the entry"
    )

    src = sub.add_parser("source", help="the source registry")
    src_sub = src.add_subparsers(dest="source_command", required=True)
    add = src_sub.add_parser("add", help="register a source and store the bytes it is checked on")
    add.add_argument("path", help="the text the quotations are checked against")
    add.add_argument(
        "--id", dest="source_id", required=True, help="the id entries cite this source by"
    )
    add.add_argument("--type", dest="source_type", required=True, help="paper, consultation, …")
    add.add_argument("--citation", required=True, help="how the source is cited in prose")
    add.add_argument("--authors", nargs="*", help="surnames, for the relayed-material flag")
    add.add_argument("--speaker", help="required for a consultation-type source")
    add.add_argument("--retrieved", help="ISO date; default today")
    add.add_argument("--url", help="where the bytes came from, so they can be regenerated")
    add.add_argument("--extraction", help="how the bytes were produced from the url")
    add.add_argument(
        "--keep-path",
        action="store_true",
        help="the row names the file in the tree (a committed fixture) rather than the cache",
    )
    src_sub.add_parser("list", help="the registered sources and whether their bytes are present")

    i = sub.add_parser("init", help="scaffold a ledger and a configuration file")
    i.add_argument("--ledger", default="ledger", help="directory to create; default `ledger`")
    i.add_argument("--force", action="store_true", help="write over an existing configuration")

    h = sub.add_parser("hook", help="the pre-commit hook that runs the checkers")
    h.add_argument("--install", action="store_true", help="write it to .git/hooks/pre-commit")
    h.add_argument(
        "--force", action="store_true", help="replace a pre-commit hook that is already there"
    )

    hs = sub.add_parser("harness", help="the coding-agent hooks and skills this package ships")
    hs_sub = hs.add_subparsers(dest="harness_command", required=True)
    hs_sub.add_parser("list", help="the agents it can write for, and where each keeps its files")
    hi = hs_sub.add_parser("install", help="write the hooks and skills into this project")
    hi.add_argument(
        "--agent",
        default="claude",
        choices=sorted(harness.TARGETS),
        help="the coding agent to write for; default `claude`",
    )
    hi.add_argument(
        "--hooks",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="`--no-hooks` writes the skills only, for a project running the hooks from "
        "somewhere else; the default installs both",
    )
    hi.add_argument(
        "--force", action="store_true", help="write over files that are there and differ"
    )

    co = sub.add_parser("corpus", help="hold the checkers to the red-team corpus")
    co.add_argument("seeds", nargs="*", help="seed name prefixes; default every seed")
    co.add_argument("-v", "--verbose", action="store_true")
    co.add_argument("--corpus", dest="corpus_dir", help="another corpus directory")

    return p


def ledger_for(args):
    # `cached` is asked of `args` rather than passed by each command, because the document
    # list it decides is built once when the ledger is opened and every checker reads it
    # from there. The commands that do not take the flag do not have the attribute
    # (L0228-documents-under-cached-are-the-ones-the-index-holds, cites-as-live).
    return open_ledger(
        root=args.root, config_path=args.config, cached=getattr(args, "cached", False)
    )


def plural(n, one, many):
    return f"{n} {one if n == 1 else many}"


def skipped_checks(ledger, cached=False):
    """What will not actually be checked from where we are pointed.

    A checker that could not run has to say so. `0 failure(s)` printed over a check that
    never happened is the one report this tool must never produce, and every line here is
    a case where the machinery is silently doing less than the README promises
    (L0121-every-check-that-did-not-run-is-named-before-the-report, cites-as-live).

    `--cached` that quietly fell back to the working tree is one of them, and the one
    that matters most in a hook: reading `show :<path>` fails identically for a path that
    is not staged and for an index nothing can parse, so the fallback is a report about
    something other than what is being committed
    (L0122-a-cached-run-that-fell-back-to-the-working-tree-says-so, cites-as-live).
    """
    notes = []
    problem = git_problem(ledger.repo) if ledger.repo else None
    if not ledger.repo:
        # Not "not a git repository": a ledger can have no repository of its own and
        # still sit inside one, and `validate` reports that case by name. Saying the
        # stronger thing here contradicted the report a line below it.
        notes.append(
            "this ledger has no git repository of its own, so the frozen-region and "
            "append-only checks did not run"
        )
    elif problem:
        # Not only `git is not on PATH`: a git that runs and fails answers None to every
        # question, and the history checks read None as `not committed yet`. A broken git
        # was quieter than a missing one until this asked.
        notes.append(f"{problem}, so the frozen-region and append-only checks did not run")
    if cached and (not ledger.repo or problem):
        notes.append("--cached had no effect: there is no git index to read")
    elif cached and (index := index_problem(ledger.repo)):
        # `git show :<path>` fails identically for a path that is not staged and for an
        # index nothing can parse, and `load_entries` reads the first as its answer. The
        # entries were read, but off the working tree — which for the pre-commit hook is
        # a report about something other than what is being committed.
        notes.append(
            f"the git index cannot be read ({index}), so --cached fell back to the "
            "working tree; what is staged was not checked"
        )
    # What the `--cached` open could not ask, in its own words. `index_problem()` above
    # asks a question whose output is empty whatever the repository holds, so it cannot
    # fail the way a listing of every tracked path can; a listing that fell back says so
    # here or nowhere (L0231-a-listing-that-fell-back-is-named-by-the-guard, cites-as-live).
    notes += [note for note in ledger.index_notes if note not in notes]
    if cached and ledger.repo and not problem:
        # The SAME listing the loader will read, not a second call: a note printed from an
        # independent call says nothing about the call that actually runs, and the one that
        # failed silently was the loader's (qe ticket f868273f36b448ab, F3).
        _reach, why = index_reach(ledger)
        note = (
            f"the index could not be listed ({why}), so --cached fell back to the "
            "working tree; what is staged was not checked"
        )
        if why and note not in notes:
            notes.append(note)
    for name, problem in ledger.unreadable_docs:
        notes.append(f"{name} {problem}")
    return notes


def guard(ledger, cached=False):
    """Print what will not be checked. Returns an exit code to stop on, or None to go on.

    An absent entries directory is a misconfigured root — the wrong `--root`, a config
    file moved away from its ledger — and stops the command at 2 rather than reporting a
    clean run over nothing. An entries directory that exists and is empty is a real
    ledger with nothing in it yet, which is a fine thing to be, so it only warns.

    A directory that exists and cannot be listed is neither: it is a ledger whose entries
    we have no way to see, and `is_dir()` says yes to it while `glob()` says it is empty.
    That combination is how a checker comes to print `0 failure(s)` over a ledger full of
    failures, so listability is established here rather than assumed.

    Ledger: (L0010-a-missing-entries-directory-stops-the-command, cites-as-live).
    """
    where = ledger.config.relative(ledger.entries_dir)
    error = entries_dir_listing_error(ledger.entries_dir)
    if isinstance(error, (FileNotFoundError, NotADirectoryError)):
        print(
            f"claims-ledger: no entries directory at {where}; nothing was checked. "
            "Is --root right, or has the ledger not been created with `claims-ledger init`?",
            file=sys.stderr,
        )
        return 2
    if error is not None:
        print(
            f"claims-ledger: the entries directory at {where} cannot be listed "
            f"({getattr(error, 'strerror', None) or error}); nothing was checked. "
            "A ledger this command cannot read is not a ledger it can report on.",
            file=sys.stderr,
        )
        return 2
    for note in skipped_checks(ledger, cached=cached):
        print(f"claims-ledger: {note}", file=sys.stderr)
    if not list_entry_files(ledger.entries_dir):
        print(f"claims-ledger: no entries under {where}", file=sys.stderr)
    return None


def report_command(name, reports, entries, ledger):
    """Print what a checker found, and exit as its findings say.

    Non-zero on a failure and zero on a flag, so a hook can be a list of these commands
    and a flag is a report a human judges rather than a gate
    (L0119-a-failure-exits-non-zero-and-a-flag-exits-zero, cites-as-live).
    """
    print_reports(reports, f"{name} ({plural(len(entries), 'entry', 'entries')})")
    return exit_code(reports)


def cmd_validate(args, ledger):
    stop = guard(ledger, cached=args.cached)
    if stop is not None:
        return stop
    entries = load_entries(ledger, cached=args.cached)
    reports = validate.run(ledger, cached=args.cached, entries=entries)
    return report_command("validate", reports, entries, ledger)


def cmd_resolve(args, ledger):
    # All three take the flag, and that is the claim: the guard so a fallback is named, the
    # load so the entries are the ones being committed, the run so a by-value anchor is held
    # to the artifact the commit will carry. Leaving one bare is the shape that survives a
    # suite: two of the three then answer about a state no commit contains — the working
    # entry against the index's artifact, or the staged entry against the working tree's —
    # and both shapes of wrong answer were measured from a bare call. A bare load passed a
    # staged entry whose anchor named nothing, at exit 0. A bare run passed an anchor the
    # index does not hold, at exit 0, in one disagreement; in the other it did fail, but
    # against the working tree, telling the author to restamp an anchor that was right. So
    # what the flag buys is that the answer is about the state being committed at all, and
    # a pass is one of the two ways it is not. The third keeps its verdict and loses only
    # the notice that the index went unread
    # (L0215-cmd-resolve-puts-the-cached-flag-to-each-of-its-three-calls, cites-as-live).
    stop = guard(ledger, cached=args.cached)
    if stop is not None:
        return stop
    entries = load_entries(ledger, cached=args.cached)
    reports = resolve.run(ledger, entries=entries, cached=args.cached)
    return report_command("resolve", reports, entries, ledger)


def cmd_references(args, ledger):
    stop = guard(ledger, cached=args.cached)
    if stop is not None:
        return stop
    entries = load_entries(ledger, cached=args.cached)
    reports = references.run(ledger, entries=entries, cached=args.cached)
    print_reports(
        reports,
        f"references ({plural(len(entries), 'entry', 'entries')}, "
        f"{plural(len(ledger.docs), 'document', 'documents')})",
    )
    return exit_code(reports)


def cmd_propagate(args, ledger):
    stop = guard(ledger, cached=args.cached)
    if stop is not None:
        return stop
    entries = entries_for(ledger, cached=args.cached, write=args.write)
    reports = propagate.run(ledger, write=args.write, entries=entries, cached=args.cached)
    return report_command("propagate", reports, entries, ledger)


def cmd_freshness(args, ledger):
    stop = guard(ledger, cached=args.cached)
    if stop is not None:
        return stop
    entries = entries_for(ledger, cached=args.cached, write=args.write)
    reports = freshness.run(ledger, write=args.write, cached=args.cached, entries=entries)
    return report_command("freshness", reports, entries, ledger)


def cmd_check(args, ledger):
    stop = guard(ledger, cached=args.cached)
    if stop is not None:
        return stop
    worst = 0
    # The entries are parsed once for the five checkers rather than once each. All five
    # now take `--cached`, so under the flag they are given one list — the staged one —
    # rather than the two this held while `references` and `propagate` had no cached mode
    # of their own. (docs/audits/ARCH-AUDIT.md, finding 4.)
    # (L0222-a-combined-run-parses-the-entries-once-into-one-list, cites-as-live)
    entries = load_entries(ledger, cached=args.cached)
    for name in CHECKERS:
        if name == "validate":
            reports = validate.run(ledger, cached=args.cached, entries=entries)
        elif name == "resolve":
            # The staged entries against the index's artifacts, the pair the commit will
            # carry. Handed the working entries instead, an entry staged with one anchor
            # and edited to another in the tree had the tree's anchor held to the index's
            # artifact — a pair no commit contains — and landed unresolved either way.
            reports = resolve.run(ledger, entries=entries, cached=args.cached)
        elif name == "references":
            reports = references.run(ledger, entries=entries, cached=args.cached)
        elif name == "propagate":
            reports = propagate.run(ledger, write=False, entries=entries, cached=args.cached)
        else:
            reports = freshness.run(ledger, write=False, cached=args.cached, entries=entries)
        print_reports(reports, name)
        worst = max(worst, exit_code(reports))
    return worst


def cmd_status(args, ledger):
    stop = guard(ledger)
    if stop is not None:
        return stop
    entries = load_entries(ledger)
    if not entries:
        print(f"no entries under {ledger.config.relative(ledger.entries_dir)}")
        return 0
    width = max(len(e.id) for e in entries)
    for e in entries:
        print(f"{e.id:<{width}}  {e.front.get('kind', '?'):<10} {e.grade:<13} {e.status()}")
    print(
        f"\n{plural(len(entries), 'entry', 'entries')} in "
        f"{ledger.config.relative(ledger.entries_dir)}"
    )
    return 0


def cmd_neighbours(args, ledger):
    """Advisory, and so exit 0 whatever it finds: the exit code of every other command
    here answers `is the ledger sound`, and a lookup that answered it with `somebody
    should read these two` would be a gate wearing a lookup's name
    (L0162-neighbours-reports-nothing-and-exits-zero, cites-as-live). Naming a target that
    is neither an entry nor a ground is a usage error and exits 2, as a mistyped path does
    everywhere else.
    """
    stop = guard(ledger)
    if stop is not None:
        return stop
    entries = load_entries(ledger)
    if args.count:
        counts = sorted(neighbours.count(ledger, entries=entries).values())
        if not counts:
            print(f"no entries under {ledger.config.relative(ledger.entries_dir)}")
            return 0
        print(
            f"{plural(len(counts), 'entry', 'entries')}: median {statistics.median(counts):g}, "
            f"mean {statistics.fmean(counts):.1f}, most {counts[-1]}, "
            f"{counts.count(0)} with none"
        )
        return 0
    if not args.target:
        print(
            "claims-ledger: neighbours needs an entry id, an entry path or a ground "
            "pointer; --count summarizes the whole ledger",
            file=sys.stderr,
        )
        return 2
    for line in neighbours.run(ledger, args.target, entries=entries):
        print(line)
    return 0


def cmd_new(args, ledger):
    path = authoring.create_entry(
        ledger,
        args.slug,
        ident=args.ident,
        kind=args.kind,
        grade=args.grade,
        author=args.author,
        supersedes=args.supersedes,
        credence=args.credence,
        resolves_when=args.resolves_when,
    )
    print(f"wrote {ledger.config.relative(path)}")
    print(
        "Fill in Assertion, Scope, Grounds, Warrant and Backing, then "
        "`claims-ledger sha --write` before the first commit; a ground's anchor may be left "
        "as `=?`, and the write fills it with the digest of the section as the tree has it."
    )
    # Said here as well as in the scaffold because this is the sentence that carries the
    # cost, and the cost is what makes the rule worth following.
    print(
        "A ground wider than the claim goes stale for edits the claim does not name, and "
        "repairing that costs a supersession. See docs/OPERATING.md."
    )
    # Named here because this is the moment the grounds are about to be chosen, and that
    # is the only moment the question has: nothing downstream asks it, by design
    # (L0168-the-scaffold-names-the-neighbour-lookup, cites-as-live).
    print(
        f"Once the Grounds are filled in, `claims-ledger neighbours {path.stem}` says "
        "which entries are already about the same code."
    )
    return 0


def cmd_lift(args, ledger):
    """Move a section's narrative prose onto the entry that rests on it.

    Dry by default. A lift deletes prose from a project's source, so the run that says
    what it would do is the one you get without asking for the other
    (L0272-a-lift-says-what-it-would-do-before-it-does-it, cites-as-live).
    """
    entries = load_entries(ledger)
    entry = by_id(entries).get(args.entry)
    if entry is None:
        print(f"claims-ledger: no entry {args.entry}", file=sys.stderr)
        return 2
    sectioned = [
        p for p in entry.ground_pointers if p.type in ledger.config.evidence_sectioned and p.section
    ]
    if not sectioned:
        print(
            f"claims-ledger: {entry.id} rests on no sectioned ground to lift from", file=sys.stderr
        )
        return 2
    if len(sectioned) > 1 and args.ground is None:
        print(
            f"claims-ledger: {entry.id} rests on {len(sectioned)} sectioned grounds; "
            "name one with --ground N",
            file=sys.stderr,
        )
        for i, p in enumerate(sectioned, start=1):
            print(f'  {i}  {p.type}: {p.target} § "{p.section}"', file=sys.stderr)
        return 2
    pointer = sectioned[(args.ground or 1) - 1]
    path = ledger.config.root / pointer.target
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"claims-ledger: {pointer.target}: {exc}", file=sys.stderr)
        return 2
    try:
        lift.refuse_unless_git_holds_it(ledger.repo, pointer.target, text)
        witness, prose, after = lift.plan(entry, pointer, text, ledger.config)
    except LedgerError as exc:
        print(f"claims-ledger: {exc}", file=sys.stderr)
        return 2
    stamp = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    blocks = [lift.passage_block(stamp, args.author, pointer, witness, x) for x in prose]
    lines = sum(len(x.splitlines()) for x in prose)
    runs = f"{len(prose)} run(s), " if len(prose) > 1 else ""
    print(f'{pointer.target} § "{pointer.section}": {runs}{lines} line(s) onto {entry.id}')
    print(f"  witness {witness}")
    if not args.write:
        print("  (nothing written; pass --write to take it)")
        shown = 0
        for i, x in enumerate(prose, start=1):
            if len(prose) > 1:
                print(f"  -- run {i}")
            for ln in x.splitlines():
                if shown >= 8:
                    break
                print(f"  | {ln}")
                shown += 1
        if lines > shown:
            print(f"  | … {lines - shown} more")
        return 0
    if args.patch:
        Path(args.patch).write_text(reverse_patch(pointer.target, after, text), encoding="utf-8")
        print(f"  reverse patch written to {args.patch}")
    # Both sides of a lift are files this command is about to rewrite, and either can be a
    # symlink out of the project; where the link leads is the caller's question
    # (L0068-a-write-is-refused-through-an-escaping-link-and-a-read-is-not, cites-as-live).
    for target in (path, entry.path):
        try:
            refuse_to_write_outside_the_root(ledger, target)
        except AuthoringError as exc:
            print(f"claims-ledger: {exc}", file=sys.stderr)
            return 2
    write_text_atomically(path, after)
    held = entry.text
    for block in blocks:
        held = lift.append_passage(held, block)
    write_text_atomically(entry.path, held)
    print(f"  written; {ledger.config.relative(entry.path)} holds {len(blocks)} passage(s)")
    return 0


def reverse_patch(rel, after, before):
    """A unified diff that puts `before` back over `after`, for a person to apply."""
    return "".join(
        difflib.unified_diff(
            after.splitlines(keepends=True),
            before.splitlines(keepends=True),
            fromfile=f"a/{rel}",
            tofile=f"b/{rel}",
        )
    )


def cmd_show(args, ledger):
    """Print the prose an entry holds — what an editor asks for when a marker is hovered."""
    entries = load_entries(ledger)
    entry = by_id(entries).get(args.entry)
    if entry is None:
        print(f"claims-ledger: no entry {args.entry}", file=sys.stderr)
        return 2
    if not entry.passages:
        print(f"{entry.id} holds no lifted prose")
        return 0
    for p in entry.passages:
        print(f"{entry.id} {p.part} · {p.timestamp} · author: {p.author}")
        print(f"  lifted: {p.lifted}")
        print()
        for ln in (p.text or "").splitlines():
            print(f"  {ln}")
        print()
    return 0


def cmd_sha(args, ledger):
    worst = 0
    for raw in args.path:
        try:
            worst = max(worst, sha_one(args, ledger, raw))
        except authoring.AuthoringError as exc:
            # Each path is its own write. Letting the first refusal out of the loop left
            # the paths after it neither written nor named, which reads as a run that
            # stopped where it says it stopped.
            # (L0124-each-path-given-to-sha-is-its-own-write, cites-as-live)
            print(f"claims-ledger: {exc}", file=sys.stderr)
            worst = 2
    return worst


def sha_one(args, ledger, raw):
    path = Path(raw)
    # A path argument is read from the current directory, as every other command-line
    # tool reads one — but with --root pointing elsewhere, the same entry named two
    # ways gave two answers and nothing said why. It says why now.
    # (L0125-a-path-argument-is-read-from-the-current-directory, cites-as-live)
    with contextlib.suppress(OSError):
        if not path.exists() and (ledger.config.root / raw).exists():
            print(
                f"claims-ledger: {raw} is read from the current directory, not from "
                f"the project root; {ledger.config.root / raw} is the entry there",
                file=sys.stderr,
            )
    declared, computed, changed, filled = authoring.restamp(
        ledger, path, write=args.write, force=args.force
    )
    for raw in filled:
        print(f"{path}: `{raw}` filled with the digest of the section as the tree has it")
    if changed:
        print(f"{path}: {declared[:12]}… → {computed[:12]}…")
        say_where_the_citation_sits(ledger, path)
        return 0
    if declared == computed:
        print(f"{path}: {computed}")
        say_where_the_citation_sits(ledger, path)
        return 0
    print(f"{path}: declared {declared[:12]}…, computed {computed[:12]}… (not written)")
    return 1


def say_where_the_citation_sits(ledger, path):
    """Report a citation of this entry that sits outside the span the entry pins, at the
    moment the entry is being written.

    `references` asks the same question of the whole ledger and is what refuses a commit.
    This asks it of one entry, here, because this is the first moment it can be asked at
    all: until the Grounds exist there is no section to be outside of, and `sha --write`
    is the step that runs once the Grounds and the citation both do, before the commit
    that lands them together
    (L0174-the-placement-question-is-asked-when-the-entry-is-written, cites-as-live).

    It prints and does not fail. What this command's exit code answers is whether the
    fingerprint was written, and a second meaning on it would make a script that reads it
    wrong about the first. Anything unreadable here means silence rather than a guess: a
    ledger that cannot be loaded is a failure `check` will report properly, and one this
    command has no business raising over a fingerprint it already wrote.
    """
    if ledger.config.citation_placement == "off":
        return
    with contextlib.suppress(LedgerError, ConfigError, OSError):
        entry = authoring.parse_entry(path)
        for report in references.misplaced_citations(ledger, only=entry.id):
            print(f"{report.part}: {report.message}")


def cmd_source(args, ledger):
    if args.source_command == "list":
        rows = load_registry(ledger.registry)
        if not rows:
            print(f"no sources in {ledger.config.relative(ledger.registry)}")
            return 0
        worst = 0
        for source_id, row in rows.items():
            _, problem = source_bytes(row, ledger)
            state = problem or "bytes present"
            print(f"{source_id}  {row.get('type', '?')}  {state}")
            worst = max(worst, 1 if problem else 0)
        return worst
    row, stored = authoring.register_source(
        ledger,
        args.source_id,
        args.path,
        args.source_type,
        args.citation,
        authors=args.authors,
        speaker=args.speaker,
        retrieved=args.retrieved,
        url=args.url,
        extraction=args.extraction,
        keep_path=args.keep_path,
    )
    print(
        f"registered {row['id']} ({row['sha256'][:12]}…) in "
        f"{ledger.config.relative(ledger.registry)}"
    )
    print(f"bytes at {ledger.config.relative(stored)}")
    return 0


def cmd_init(args, _ledger):
    root = Path(args.root or Path.cwd()).resolve()
    ledger_dir = root / args.ledger
    config_path = root / "claims-ledger.toml"
    if config_path.exists() and not args.force:
        print(f"{config_path} already exists; pass --force to write over it", file=sys.stderr)
        return 1
    registry = ledger_dir / "sources.jsonl"
    ignore = ledger_dir / "cache" / ".gitignore"
    # `init` creates the root, so it was allowed to skip the guard every other write in
    # this package asks — and skipping it meant a symlink planted at any of these four
    # names sent the scaffolder outside the project, exit 0, printing the in-root path it
    # had not written to. The root is resolved above, so the question the guard asks is
    # one that can be answered here: where does this name really lead.
    # (L0126-init-asks-the-containment-question-of-every-name-it-writes, cites-as-live)
    for path, what in (
        (ledger_dir, "the ledger directory"),
        (config_path, "the configuration"),
        (ignore, "the cache .gitignore"),
        (registry, "the source registry"),
    ):
        outside = leaves_root(root, path)
        if outside is not None:
            print(
                f"claims-ledger: {what} at {path} leads to {outside}, outside the "
                f"project root {root}; nothing is written through a link that leaves "
                "the project",
                file=sys.stderr,
            )
            return 2
    for path, what in ((config_path, "the configuration"), (ignore, "the cache .gitignore")):
        # Opening a FIFO for writing blocks until a reader appears, which is a wedged job
        # with no output at all. The registry is only written when it does not exist, and
        # `--force` is what makes the configuration a write over something already there.
        # (L0127-init-writes-its-files-only-onto-regular-files, cites-as-live)
        if os.path.lexists(path) and file_problem(path, what) is not None:
            print(
                f"claims-ledger: {path} is not a regular file; {what} is written to a "
                "plain file, and this one would not be one",
                file=sys.stderr,
            )
            return 2
    try:
        # A regular file already at `ledger/entries`, a read-only project directory: a
        # scaffolder run in the wrong place fails in ordinary ways, and none of them is a
        # bug in this package to be reported.
        (ledger_dir / "entries").mkdir(parents=True, exist_ok=True)
        cache = ledger_dir / "cache"
        cache.mkdir(parents=True, exist_ok=True)
        write_text_atomically(ignore, CACHE_IGNORE)
        if not registry.exists():
            write_text_atomically(registry, "")
        write_text_atomically(
            config_path, CONFIG_TEMPLATE.format(ledger=args.ledger, code=CODE_RECIPE)
        )
    except OSError as exc:
        print(
            f"claims-ledger: cannot scaffold the ledger under {ledger_dir} "
            f"({exc.strerror or exc}: {exc.filename or ledger_dir})",
            file=sys.stderr,
        )
        return 2
    print(f"wrote {config_path}")
    print(f"created {ledger_dir}/entries, {ledger_dir}/cache and {registry}")
    print("Next: `claims-ledger new <slug>`, then `claims-ledger check`.")
    return 0


def hooks_dir(repo):
    """(the directory git runs hooks out of, why it could not be asked).

    `.git/hooks` is a guess, and it is wrong in three ways this package cannot afford.
    `core.hooksPath` moves the directory anywhere, and an install into `.git/hooks` under
    it reported `installed …` and exit 0 for a file git will never execute — a gate that
    does not exist, announced as installed, which is the failure this package exists to
    refuse and is HIGH-57's own class at the surface HIGH-57 fixed. In a linked worktree
    and under `--separate-git-dir`, `.git` is a *file*, so the install failed with
    `Not a directory` at a path that was never the right one.

    `git rev-parse --git-path hooks` answers all three, because it is the question git
    asks itself. Resolved against the repository, since git answers relative to it
    (L0128-the-hooks-directory-is-asked-of-version-control, cites-as-live).
    """
    answer = git_call(repo, "rev-parse", "--git-path", "hooks")
    if not answer.ok or not answer.out.strip():
        return None, (
            f"git could not say where this repository keeps its hooks ({answer.why}); "
            "the hook was not installed, because a hook installed where git does not "
            "look is a check that never runs"
        )
    return Path(repo) / answer.out.strip(), None


def cmd_hook(args, ledger):
    if not args.install:
        print(hook_text(), end="")
        return 0
    if not ledger.repo:
        print("not a git repository; nothing to install into", file=sys.stderr)
        return 1
    hooks, why = hooks_dir(ledger.repo)
    if hooks is None:
        print(f"claims-ledger: {why}", file=sys.stderr)
        return 2
    path = hooks / "pre-commit"
    try:
        # `lexists`, because a symlink to nothing is still something someone put there:
        # `exists()` said no to it and the install wrote through it. Asked before the
        # containment guard so that a deliberate `pre-commit -> ../../shared/pre-commit`
        # — a team sharing one hook — is met with "leaving it alone" and the hook text,
        # which is what it was always met with, rather than with an accusation.
        #
        # `--force` is the way past it, and without one this was the only installer here a
        # project could not update: a checkout that ran `--install` once kept that hook
        # forever, however far the shipped one moved on. The refusal says which of the two
        # cases it is, because they want different things of the reader — an older copy of
        # this hook wants `--force`, and somebody's own hook wants a decision. A marker
        # line rather than a comparison of the whole text, which cannot be made: the
        # interpreter is interpolated, so no two installs need match byte for byte.
        # (L0224-an-existing-hook-is-left-alone-unless-the-install-is-forced, cites-as-live)
        if os.path.lexists(path) and not args.force:
            ours = (
                " It is an older copy of this hook; `--force` replaces it."
                if is_our_hook(path)
                else " It is not a copy of this hook, so replacing it is a decision to make."
            )
            print(
                f"{path} exists; leaving it alone.{ours} Its contents would be:\n",
                file=sys.stderr,
            )
            print(hook_text(), end="")
            return 1
        # Whatever the write lands on may be reached through a link the repository does not
        # control — the hooks directory itself being one. A dangling `pre-commit ->
        # /tmp/x.sh` took a mode-755 shell script outside, exit 0, naming the in-root path
        # it had not written to; a `hooks -> /tmp` does the same one level up, and
        # `lexists` above cannot see that one. Asked under `--force` as well, and that is
        # what keeps a shared hook shared: the write resolves a symlink before it replaces,
        # so forcing over `pre-commit -> ../../shared/pre-commit` would rewrite the team's
        # file rather than this repository's link to it. Refused, with the link named.
        # (L0130-the-hook-is-not-installed-through-an-escaping-link, cites-as-live)
        outside = leaves_root(hooks, path)
        if outside is not None:
            print(
                f"claims-ledger: {path} leads to {outside}, outside the hooks directory "
                f"{hooks}; the hook is not installed through a link that leaves it",
                file=sys.stderr,
            )
            return 2
        hooks.mkdir(parents=True, exist_ok=True)
        write_text_atomically(path, hook_text(), mode=0o755)
    except OSError as exc:
        # A read-only .git/hooks is an ordinary thing in a locked-down or shared checkout.
        print(
            f"claims-ledger: cannot install the hook at {path} ({exc.strerror or exc})",
            file=sys.stderr,
        )
        return 2
    print(f"installed {path}")
    return 0


def cmd_harness(args, _ledger):
    """Print where each agent's files would go, or write them there.

    No ledger is opened. Installing the harness is a thing to do in a project that has
    not got one yet — the hooks are what tells a session the ledger exists, and an
    installer that failed on a missing configuration would be asking for the thing it is
    there to help set up (L0185-the-harness-installs-without-a-ledger, cites-as-live).
    """
    if args.harness_command == "list":
        for name, target in sorted(harness.TARGETS.items()):
            print(f"{name}  ({target.label})")
            print(f"  skills   {target.skills}/<skill>/SKILL.md")
            print(f"  hooks    {target.hooks}/")
            note = " (the only file it reads hooks from)" if target.user_home else ""
            print(f"  wiring   {target.wiring}{note}")
        return 0

    root = Path(args.root or Path.cwd()).resolve()
    target = harness.TARGETS[args.agent]
    try:
        written = harness.install(target, root, hooks=args.hooks, force=args.force)
        wiring = harness.install_wiring(target, root)
    except harness.MissingResources as exc:
        print(f"claims-ledger: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        # A read-only checkout, a full disk: ordinary failures of a write, and none of
        # them a bug in this package to be reported as one.
        print(
            f"claims-ledger: cannot install the harness under {root} ({exc.strerror or exc}: "
            f"{exc.filename or root})",
            file=sys.stderr,
        )
        return 2
    return report_install(target, root, written, wiring)


def report_install(target, root, written, wiring):
    """Say of every file what happened to it, and exit on the worst of it.

    Three states and three meanings: `wrote` did something, `present` found the same
    bytes already there and did nothing, and `differs` found something else and left it
    alone. An install that changed nothing because everything was already in place exits
    0 — running it twice is not an error — and one that left a file alone exits 1, because
    the project does not have what it was asked for and saying otherwise would be the one
    report this package must never print
    (L0186-an-install-that-changed-nothing-exits-zero-and-one-that-skipped-does-not,
    cites-as-live).
    """
    worst = 0
    for item in written + ([wiring] if wiring else []):
        # Relative where that reads better, absolute where the file is not in the project
        # at all — which is codex's wiring, and the one path a reader must not misread.
        where = os.path.relpath(item.path, root) if item.path.is_relative_to(root) else item.path
        if item.state == "wrote":
            print(f"wrote      {where}")
        elif item.state == "present":
            print(f"present    {where}")
        elif item.state == "differs":
            print(
                f"left alone {where} (it differs; pass --force to write over it)", file=sys.stderr
            )
            worst = max(worst, 1)
        else:
            print(f"left alone {where} ({item.state})", file=sys.stderr)
            worst = max(worst, 1 if item.state == "exists" else 2)
    if target.user_home and wiring is not None and wiring.state != "differs":
        print(
            f"\n{target.label} reads hooks from {wiring.path} and from nowhere else, and "
            "asks you to review them before it runs any: they are inert until you do."
        )
    if wiring is not None and wiring.state == "exists":
        print(
            f"\n{wiring.path} is already there and is not edited by this command. It needs:\n",
            file=sys.stderr,
        )
        print(harness.wiring_json(target, root))
    return worst


def cmd_corpus(args, _ledger):
    """The red-team corpus, which needs version control and says so rather than passing.

    The seeds are applied as commits in a temporary repository, so without git there is
    nothing to run them against — and a corpus run that reported success over seeds it
    never applied would be the one report this tool must never produce, about the very
    thing that proves the checkers
    (L0131-the-corpus-refuses-to-run-without-version-control, cites-as-live).
    """
    if not git_available():
        print(
            "claims-ledger: git is not on PATH, and the corpus cannot run without it: "
            "its history seeds are applied as commits in a temporary repository. "
            "Nothing was checked.",
            file=sys.stderr,
        )
        return 2
    from .corpus import run as corpus_run

    argv = list(args.seeds)
    if args.verbose:
        argv.append("-v")
    if args.corpus_dir:
        argv += ["--corpus", args.corpus_dir]
    return corpus_run.main(argv)


# `init` has no ledger to open yet, and `corpus` brings its own; neither may fail on a
# configuration that is not there.
NO_LEDGER = {"init", "corpus", "harness"}


def cmd_renumber(args, ledger):
    """Plan the rewrite, say what it would do, and carry it out only when asked.

    A collision found and not repaired exits non-zero, because it is a finding: the two
    branches as they stand cannot both land, and a guard or a script asking this question
    needs the answer in the exit code rather than in the prose
    (L0244-a-collision-found-and-not-repaired-exits-non-zero, cites-as-live).

    `--on-merge` is the same question asked by a merge guard, and what it does is the
    project's to configure: `off` says nothing, `refuse` reports and stops the merge, and
    `rewrite` carries the renumber out and lets it proceed
    (L0243-the-merge-time-policy-is-configured-and-defaults-to-refusing, cites-as-live).

    Nothing is written without `--write` or that configured `rewrite`, and with it nothing
    is written while the working
    tree has changes of its own or while another checkout has the branch out: the rewrite
    ends by moving a ref and resetting the checkout onto it, and both of those are ways to
    lose work that was never committed
    (L0241-a-rewrite-refuses-a-dirty-tree-and-a-branch-another-checkout-holds,
    cites-as-live).
    """
    if args.on_merge and ledger.config.merge_renumber == "off":
        return 0
    try:
        renumbering = renumber.plan(ledger, args.onto, args.branch)
    except renumber.RepositoryUnreadable as exc:
        # Not "not its business": this is the one refusal that means the question was
        # never answered, and a guard that allows a merge out of ignorance is the false
        # pass the whole package refuses.
        # (L0249-a-guard-that-could-not-read-the-repository-does-not-allow-the-merge, cites-as-live)
        print(f"claims-ledger: {exc}", file=sys.stderr)
        return 1 if args.on_merge else 2
    except renumber.RenumberError as exc:
        if args.on_merge:
            return 0  # a guard asks about every merge; a branch it cannot plan is not its business
        print(f"claims-ledger: {exc}", file=sys.stderr)
        return 2
    if renumbering.empty:
        for line in renumber.describe(renumbering, []):
            print(line)
        return 0
    refused = renumber.refusals(ledger, renumbering)
    for line in renumber.describe(renumbering, refused):
        print(line)
    write = args.write
    if args.on_merge:
        if ledger.config.merge_renumber == "refuse":
            print(
                "claims-ledger: merging this branch would land two entries answering to one "
                "number, which `validate` fails on from that commit onward. Rewrite the "
                "branch first: `claims-ledger renumber --onto "
                f"{args.onto} --branch {args.branch} --write`.",
                file=sys.stderr,
            )
            return 1
        write = True
    if not write:
        print("nothing was written; `--write` carries it out")
        return 1
    if refused and not args.force:
        print(
            "claims-ledger: nothing was written; `--force` rewrites anyway",
            file=sys.stderr,
        )
        return 2
    try:
        renumber.branch_ref(ledger.repo, renumbering.ref)
        held = renumber.checkout_holding(ledger.repo, renumbering.ref, renumbering.commits)
        if held is not None:
            raise renumber.RenumberError(
                f"`{renumbering.ref}` is checked out at {held}; rewriting it would leave "
                "that checkout on commits no ref names"
            )
        if renumber.working_tree_changes(ledger.repo):
            raise renumber.RenumberError(
                "the working tree has changes that are not committed, and the rewrite ends "
                "by resetting this checkout onto the commits it wrote; commit or stash them"
            )
        with tempfile.TemporaryDirectory() as scratch:
            tip = renumber.rewrite(ledger, renumbering, Path(scratch) / "index")
        renumber.move_branch(ledger.repo, renumbering, tip)
    except renumber.RenumberError as exc:
        print(f"claims-ledger: {exc}", file=sys.stderr)
        return 2
    print(f"{renumbering.ref} now names {tip[:7]}; {len(renumbering.commits)} commit(s) rewritten")
    print("The ids moved, so run `claims-ledger check` before merging.")
    return 0


COMMANDS = {
    "validate": cmd_validate,
    "resolve": cmd_resolve,
    "references": cmd_references,
    "propagate": cmd_propagate,
    "freshness": cmd_freshness,
    "check": cmd_check,
    "status": cmd_status,
    "neighbours": cmd_neighbours,
    "new": cmd_new,
    "lift": cmd_lift,
    "show": cmd_show,
    "sha": cmd_sha,
    "source": cmd_source,
    "init": cmd_init,
    "renumber": cmd_renumber,
    "hook": cmd_hook,
    "harness": cmd_harness,
    "corpus": cmd_corpus,
}


def soften_output_encoding():
    """Make the output streams tolerate what they cannot encode.

    Under an ASCII locale, printing the schema's own `·` separator raises
    UnicodeEncodeError — and it raises on the path that was about to explain why a check
    failed, replacing the diagnostic with `this is a bug`. `backslashreplace` keeps the
    character visible as an escape rather than taking the message down with it
    (L0132-a-report-survives-a-locale-that-cannot-encode-it, cites-as-live).
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:  # pytest's capture, a plain file object
            continue
        with contextlib.suppress(Exception):
            reconfigure(errors="backslashreplace")


def main(argv=None):
    """The entry point, and the last place an exception can be turned into a message.

    Nothing reaches a stranger as a traceback: an unexpected exception prints its type
    and its message, says plainly that it is a bug, gives the address to report it at,
    and names the environment variable that puts the traceback back for whoever is
    debugging (L0133-an-unexpected-error-is-a-message-and-never-a-traceback,
    cites-as-live).

    A closed reader is not an error at all — `status | head` is an ordinary thing to
    type — so stdout is pointed at the null device before returning, and the code
    returned is the one a shell reports for the same signal
    (L0134-a-closed-reader-exits-as-the-shell-would-report-it, cites-as-live).

    `init`, `corpus` and `harness` are dispatched without opening a ledger, because none
    of them may fail on a configuration that is not there yet or that belongs to someone
    else (L0135-init-and-corpus-open-no-ledger, cites-as-live).
    """
    soften_output_encoding()
    args = build_parser().parse_args(argv)
    try:
        ledger = None if args.command in NO_LEDGER else ledger_for(args)
        code = COMMANDS[args.command](args, ledger)
        sys.stdout.flush()
        return code
    except (ConfigError, LedgerError, authoring.AuthoringError) as exc:
        print(f"claims-ledger: {exc}", file=sys.stderr)
        return 2
    except BrokenPipeError:
        # `claims-ledger status | head`. Point stdout at devnull so the interpreter's
        # own shutdown flush cannot raise a second time and print over the reader.
        with contextlib.suppress(OSError):
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 141  # 128 + SIGPIPE, what a shell reports for the same thing
    except KeyboardInterrupt:
        print("claims-ledger: interrupted", file=sys.stderr)
        return 130
    except Exception as exc:  # never a traceback at a stranger
        print(f"claims-ledger: unexpected {type(exc).__name__}: {exc}", file=sys.stderr)
        print(
            "claims-ledger: this is a bug. Please report it at "
            "https://github.com/Ybx-jp/claims-ledger/issues with the command you ran; "
            "CLAIMS_LEDGER_TRACEBACK=1 prints the traceback.",
            file=sys.stderr,
        )
        if os.environ.get("CLAIMS_LEDGER_TRACEBACK"):
            raise
        return 2


if __name__ == "__main__":
    sys.exit(main())
