"""The `claims-ledger` command.

Five checkers, an authoring side, and the corpus that proves the checkers. Every
subcommand exits non-zero on a failure and zero on a flag, so a hook can be a list of
commands and a flag is a report a human judges rather than a gate
(L0119-a-failure-exits-non-zero-and-a-flag-exits-zero, cites-as-live).
"""

from __future__ import annotations

import argparse
import contextlib
import os
import shlex
import statistics
import sys
from pathlib import Path

from . import (
    __version__,
    authoring,
    freshness,
    neighbours,
    propagate,
    references,
    resolve,
    validate,
)
from .config import ConfigError, leaves_root
from .schema import (
    LedgerError,
    entries_dir_listing_error,
    exit_code,
    file_problem,
    git_available,
    git_call,
    git_problem,
    index_problem,
    list_entry_files,
    load_entries,
    load_registry,
    open_ledger,
    print_reports,
    source_bytes,
    write_text_atomically,
)

CHECKERS = ("validate", "resolve", "references", "propagate", "freshness")

# Ledger: (L0001-hook-names-the-interpreter-absolutely, cites-as-live). The hook asks
# each checker for the index wherever that checker has a `--cached` of its own, so a
# drift that is staged and then reverted in the working tree cannot commit silently
# (L0120-the-hook-reads-the-index-wherever-a-checker-can, cites-as-live).
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
# `resolve`, `references` and `propagate` have no `--cached` of their own yet, so this
# hook still reads the working tree for those three; giving all five the flag is a wider
# fix than this one, and out of this pass's budget to audit.
set -e
{python} -m claims_ledger validate --cached
{python} -m claims_ledger resolve
{python} -m claims_ledger references
{python} -m claims_ledger propagate
{python} -m claims_ledger freshness --cached
"""


def hook_text(python=None):
    return HOOK_TEMPLATE.format(python=shlex.quote(python or sys.executable))


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
# code = '^(?:def|class) +{{name}}'

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

    sub.add_parser("resolve", help="pointers resolve and quotations are spans of their sources")
    sub.add_parser("references", help="citation acts agree with statuses, both directions")

    pr = sub.add_parser("propagate", help="dependents of fallen entries carry the contested flag")
    pr.add_argument("--write", action="store_true", help="append the missing verdicts")

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

    s = sub.add_parser(
        "sha", help="the verbatim fingerprint of an entry, recomputed from Scope and Backing"
    )
    s.add_argument("path", nargs="+")
    s.add_argument("--write", action="store_true", help="rewrite the declared value")
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

    co = sub.add_parser("corpus", help="hold the checkers to the red-team corpus")
    co.add_argument("seeds", nargs="*", help="seed name prefixes; default every seed")
    co.add_argument("-v", "--verbose", action="store_true")
    co.add_argument("--corpus", dest="corpus_dir", help="another corpus directory")

    return p


def ledger_for(args):
    return open_ledger(root=args.root, config_path=args.config)


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
    stop = guard(ledger)
    if stop is not None:
        return stop
    entries = load_entries(ledger)
    reports = resolve.run(ledger, entries=entries)
    return report_command("resolve", reports, entries, ledger)


def cmd_references(args, ledger):
    stop = guard(ledger)
    if stop is not None:
        return stop
    entries = load_entries(ledger)
    reports = references.run(ledger, entries=entries)
    print_reports(
        reports,
        f"references ({plural(len(entries), 'entry', 'entries')}, "
        f"{plural(len(ledger.docs), 'document', 'documents')})",
    )
    return exit_code(reports)


def cmd_propagate(args, ledger):
    stop = guard(ledger)
    if stop is not None:
        return stop
    entries = load_entries(ledger)
    reports = propagate.run(ledger, write=args.write, entries=entries)
    return report_command("propagate", reports, entries, ledger)


def cmd_freshness(args, ledger):
    stop = guard(ledger, cached=args.cached)
    if stop is not None:
        return stop
    entries = load_entries(ledger, cached=args.cached)
    reports = freshness.run(ledger, write=args.write, cached=args.cached, entries=entries)
    return report_command("freshness", reports, entries, ledger)


def cmd_check(args, ledger):
    stop = guard(ledger, cached=args.cached)
    if stop is not None:
        return stop
    worst = 0
    # The entries are parsed once for the five checkers rather than once each. Two lists
    # and not one: under `--cached` `validate` and `freshness` read what is staged and the
    # other three read the working tree, which is the difference `--cached` exists to
    # make. (ARCH-AUDIT.md, finding 4.)
    # (L0123-check-parses-the-entries-once-into-two-lists, cites-as-live)
    working = load_entries(ledger)
    staged = load_entries(ledger, cached=True) if args.cached else working
    for name in CHECKERS:
        if name == "validate":
            reports = validate.run(ledger, cached=args.cached, entries=staged)
        elif name == "resolve":
            reports = resolve.run(ledger, entries=working)
        elif name == "references":
            reports = references.run(ledger, entries=working)
        elif name == "propagate":
            reports = propagate.run(ledger, write=False, entries=working)
        else:
            reports = freshness.run(ledger, write=False, cached=args.cached, entries=staged)
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
        "`claims-ledger sha --write` before the first commit."
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
    declared, computed, changed = authoring.restamp(
        ledger, path, write=args.write, force=args.force
    )
    if changed:
        print(f"{path}: {declared[:12]}… → {computed[:12]}…")
        return 0
    if declared == computed:
        print(f"{path}: {computed}")
        return 0
    print(f"{path}: declared {declared[:12]}…, computed {computed[:12]}… (not written)")
    return 1


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
        write_text_atomically(config_path, CONFIG_TEMPLATE.format(ledger=args.ledger))
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
        # (L0129-an-existing-hook-is-left-alone-and-the-text-is-printed, cites-as-live)
        if os.path.lexists(path):
            print(f"{path} exists; leaving it alone. Its contents would be:\n", file=sys.stderr)
            print(hook_text(), end="")
            return 1
        # Nothing is there, so anything the write lands on is reached through a link the
        # repository does not control — the hooks directory itself being one. A dangling
        # `pre-commit -> /tmp/x.sh` took a mode-755 shell script outside, exit 0, naming
        # the in-root path it had not written to; a `hooks -> /tmp` does the same one
        # level up, and `lexists` above cannot see that one.
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
NO_LEDGER = {"init", "corpus"}

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
    "sha": cmd_sha,
    "source": cmd_source,
    "init": cmd_init,
    "hook": cmd_hook,
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

    `init` and `corpus` are dispatched without opening a ledger, because neither may fail
    on a configuration that is not there yet or that belongs to someone else
    (L0135-init-and-corpus-open-no-ledger, cites-as-live).
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
