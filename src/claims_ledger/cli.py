"""The `claims-ledger` command.

Five checkers, an authoring side, and the corpus that proves the checkers. Every
subcommand exits non-zero on a failure and zero on a flag, so a hook can be a list of
commands and a flag is a report a human judges rather than a gate.
"""

from __future__ import annotations

import argparse
import contextlib
import os
import shlex
import sys
from pathlib import Path

from . import __version__, authoring, freshness, propagate, references, resolve, validate
from .config import ConfigError
from .schema import (
    LedgerError,
    entries_dir_listing_error,
    exit_code,
    file_problem,
    git_available,
    git_problem,
    list_entry_files,
    load_entries,
    load_registry,
    open_ledger,
    print_reports,
    source_bytes,
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
set -e
{python} -m claims_ledger validate --cached
{python} -m claims_ledger resolve
{python} -m claims_ledger references
{python} -m claims_ledger propagate
{python} -m claims_ledger freshness
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
# `(A0001-slug, cites-as-live)` and is held to the entry's current status at every check.
documents = ["*.md", "docs/*.md"]
# document-excludes = []

# The named artifacts an entry may rest on. A `sectioned` type is written
# `lab: <path> § "<section>" @<commit>`; a plain one `experiment: <path> @<commit>`.
# The pin is what `freshness` compares against the working tree, so a pin that names a
# commit goes stale visibly and one that names a branch never can. `@working` opts out.
evidence-sectioned = ["lab"]
evidence-plain = ["experiment"]

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

    c = sub.add_parser("check", help="run all five checkers")
    c.add_argument("--cached", action="store_true", help="read staged entries from the git index")

    sub.add_parser("status", help="every entry with its kind, grade and derived status")

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
    a case where the machinery is silently doing less than the README promises.
    """
    notes = []
    problem = git_problem(ledger.repo) if ledger.repo else None
    if not ledger.repo:
        notes.append(
            "not a git repository, so the frozen-region and append-only checks did not run"
        )
    elif problem:
        # Not only `git is not on PATH`: a git that runs and fails answers None to every
        # question, and the history checks read None as `not committed yet`. A broken git
        # was quieter than a missing one until this asked.
        notes.append(f"{problem}, so the frozen-region and append-only checks did not run")
    if cached and (not ledger.repo or problem):
        notes.append("--cached had no effect: there is no git index to read")
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
    reports = validate.run(ledger, cached=args.cached)
    return report_command("validate", reports, load_entries(ledger), ledger)


def cmd_resolve(args, ledger):
    stop = guard(ledger)
    if stop is not None:
        return stop
    reports = resolve.run(ledger)
    return report_command("resolve", reports, load_entries(ledger), ledger)


def cmd_references(args, ledger):
    stop = guard(ledger)
    if stop is not None:
        return stop
    entries = load_entries(ledger)
    reports = references.run(ledger)
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
    reports = propagate.run(ledger, write=args.write)
    return report_command("propagate", reports, load_entries(ledger), ledger)


def cmd_freshness(args, ledger):
    stop = guard(ledger)
    if stop is not None:
        return stop
    reports = freshness.run(ledger, write=args.write)
    return report_command("freshness", reports, load_entries(ledger), ledger)


def cmd_check(args, ledger):
    stop = guard(ledger, cached=args.cached)
    if stop is not None:
        return stop
    worst = 0
    for name in CHECKERS:
        if name == "validate":
            reports = validate.run(ledger, cached=args.cached)
        elif name == "resolve":
            reports = resolve.run(ledger)
        elif name == "references":
            reports = references.run(ledger)
        elif name == "propagate":
            reports = propagate.run(ledger, write=False)
        else:
            reports = freshness.run(ledger, write=False)
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
    return 0


def cmd_sha(args, ledger):
    worst = 0
    for raw in args.path:
        path = Path(raw)
        # A path argument is read from the current directory, as every other command-line
        # tool reads one — but with --root pointing elsewhere, the same entry named two
        # ways gave two answers and nothing said why. It says why now.
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
        elif declared == computed:
            print(f"{path}: {computed}")
        else:
            print(f"{path}: declared {declared[:12]}…, computed {computed[:12]}… (not written)")
            worst = 1
    return worst


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
    for path, what in ((config_path, "the configuration"), (ignore, "the cache .gitignore")):
        # Opening a FIFO for writing blocks until a reader appears, which is a wedged job
        # with no output at all. The registry is only written when it does not exist, and
        # `--force` is what makes the configuration a write over something already there.
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
        ignore.write_text(CACHE_IGNORE, encoding="utf-8")
        if not registry.exists():
            registry.write_text("", encoding="utf-8")
        config_path.write_text(CONFIG_TEMPLATE.format(ledger=args.ledger), encoding="utf-8")
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


def cmd_hook(args, ledger):
    if not args.install:
        print(hook_text(), end="")
        return 0
    if not ledger.repo:
        print("not a git repository; nothing to install into", file=sys.stderr)
        return 1
    hooks = Path(ledger.repo) / ".git" / "hooks"
    path = hooks / "pre-commit"
    try:
        hooks.mkdir(parents=True, exist_ok=True)
        if path.exists():
            print(f"{path} exists; leaving it alone. Its contents would be:\n", file=sys.stderr)
            print(hook_text(), end="")
            return 1
        path.write_text(hook_text(), encoding="utf-8")
        path.chmod(0o755)
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
    character visible as an escape rather than taking the message down with it.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:  # pytest's capture, a plain file object
            continue
        with contextlib.suppress(Exception):
            reconfigure(errors="backslashreplace")


def main(argv=None):
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
