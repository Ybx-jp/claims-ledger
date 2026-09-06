"""Run the four checkers over every seed in the red-team corpus and hold them to each
seed's expected.json, under the contract in README.md:

- every `fail` and `flag` row is produced by the named checker at the named place;
- every checker not named in a non-pass row exits clean, and a checker that is named
  produces nothing the rows do not name — an unlisted trip is a finding about the seed
  or the checker, never a bonus catch;
- `review` rows bind nothing;
- history seeds (`commits/`) are applied as successive commits in a fresh repository
  and their rows name the commit they apply to.

Each seed is checked as if its entries/ and docs/ were the whole ledger, with
sources.jsonl and fixtures/ shared from the corpus root and evidence paths resolved
against it. Entries are copied to a temporary directory first, so a checker that writes
(propagate --write) cannot touch the corpus; here propagate runs read-only.

Run:  claims-ledger corpus [-v] [SEED ...]
      --corpus <dir> points the runner at another corpus directory (the tests use a
      tampered copy to show the runner can fail); so does LEDGER_CORPUS.
Exit 1 if any seed fails.
"""

from __future__ import annotations

import functools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

from .. import freshness, propagate, references, resolve, validate
from ..config import Config
from ..schema import GIT_TIMEOUT, Ledger, LedgerError, unreadable_document

CORPUS = Path(__file__).resolve().parent

CHECKERS = {
    "validate": validate.run,
    "resolve": resolve.run,
    "references": references.run,
    # The two that need an argument bound: here they only report, never write.
    "propagate": functools.partial(propagate.run, write=False),
    "freshness": functools.partial(freshness.run, write=False),
}
WHERE_RE = re.compile(r"^(?:commit (\d+),?\s*)?(.*)$")
ENTRY_RE = re.compile(r"^([A-Z]\d+)\s*(.*)$")


def corpus_root(override=None):
    """The corpus directory. The tests point the runner at a tampered copy to check that
    the runner can fail, so the location is an input rather than a constant."""
    return Path(override or os.environ.get("LEDGER_CORPUS") or CORPUS).resolve()


def corpus_config(root, entries_dir):
    """The configuration the seeds are written against: the corpus directory is the
    project root, its sources.jsonl is the registry, the bytes are committed fixtures
    rather than a cache, and the series `C` and `P` stand in for a quarantined archive."""
    return Config(
        root=root,
        ledger_dir=root,
        entries_dir=entries_dir,
        registry=root / "sources.jsonl",
        cache=None,
        archived_prefixes=("C", "P"),
    )


def parse_where(where):
    """(commit, entry prefix, part) from an expectation row's `where`."""
    m = WHERE_RE.match(where.strip())
    if m is None:  # every group in the pattern is optional, so this cannot happen today
        raise ValueError(f"expectation row has an unparseable `where`: {where!r}")
    commit, rest = m.group(1), m.group(2).strip()
    em = ENTRY_RE.match(rest)
    if em:
        return commit, em.group(1), em.group(2).strip()
    return commit, None, rest


def matches(report, commit, entry, part, message=None):
    """Whether a report is the one an expectation row names.

    The place is compared exactly. A row that named a prefix of it — `A0001 frontmatter`
    against `frontmatter credence` and `frontmatter resolves_when` — was satisfied by
    either of the two rules it was meant to bind, so deleting one of them left the corpus
    green. A row names the rule's place or it names nothing.

    `message` is a row's optional handle on the rule itself, as a substring of what the
    report said. The place is where a rule fires and not which rule it is, so a rule whose
    place another rule can also occupy — or one whose report would survive being emptied
    of everything but its outcome — is named here as well.

    An empty string is not a substring that pins anything: `"" in x` is true of every
    `x`, so a row that wrote `"message": ""` would otherwise bind exactly as loosely as
    one that omitted the key — but silently, since it looks pinned. Only `None` — the key
    left out — means "the place alone is enough."
    """
    if report.commit != commit or report.entry != entry:
        return False
    if report.part.casefold() != part.casefold():
        return False
    if message is None:
        return True
    return bool(message) and message.casefold() in report.message.casefold()


def seed_ledger(root, staged, repo=None):
    """The seed's `docs/` as `open_ledger` would present it: the documents that read, and
    separately the ones that did not.

    A document that could not be opened is not an empty document, and `references` has a
    rule saying so. Handing every path over as though it had been read would have made
    that rule unreachable from the corpus — a rule about not silently passing that no
    seed could hold.
    """
    docs, unreadable = [], []
    for path in sorted((staged / "docs").glob("*.md")) if (staged / "docs").is_dir() else []:
        name = f"docs/{path.name}"
        if not path.is_file():
            unreadable.append((name, "is not a regular file; it was not checked"))
        elif (problem := unreadable_document(path)) is not None:
            unreadable.append((name, f"{problem}; its citations were not checked"))
        else:
            docs.append((name, path))
    return Ledger(
        config=corpus_config(root, staged / "entries"),
        docs=docs,
        repo=repo,
        unreadable_docs=unreadable,
    )


# A history seed cannot know the object ids of the commits the runner is about to make,
# so an entry that must rest on one writes `@commit01` and the runner substitutes the
# real short id of that state once it exists. The substitution happens before the state
# is committed, so what git records is what the checkers read: an entry whose frozen
# region is stable across every later commit, exactly as a hand-written pin would be.
PIN_RE = re.compile(r"@commit(\d+)")


def stage(src, dst, pins=None):
    for name in ("entries", "docs"):
        if (dst / name).exists():
            shutil.rmtree(dst / name)
        if (src / name).is_dir():
            # `copyfile` rather than the default `copy2`, which preserves the source's
            # mtime. Git's index caches (mtime, size) and skips reading a file whose pair
            # is unchanged, so a seed state that edits a line without changing its length
            # — `0.041` to `0.991` — staged as a file git believed it had already seen,
            # `git add -A` picked up nothing, and the commit failed with `nothing to
            # commit` rather than with anything naming the cause.
            shutil.copytree(src / name, dst / name, copy_function=shutil.copyfile)
    if not pins:
        return
    for path in sorted((dst).glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        swapped = PIN_RE.sub(lambda m: "@" + pins.get(m.group(1), m.group(0)[1:]), text)
        if swapped != text:
            path.write_text(swapped, encoding="utf-8")


def git(repo, *args):
    """A git command the corpus needs to have worked — its history seeds are commits, so
    a failure here is not a finding about a seed, it is the corpus being unable to run.
    Reported as such, rather than raised through the CLI's catch-all as a bug report."""
    try:
        subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "-c",
                "user.name=corpus",
                "-c",
                "user.email=corpus@example",
                "-c",
                "commit.gpgsign=false",
                *args,
            ],
            check=True,
            capture_output=True,
            text=True,
            # As in schema.git(): `text=True` alone decodes with the locale's codec, and a
            # git that blocks would hang the corpus with no way out.
            encoding="utf-8",
            errors="replace",
            timeout=GIT_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        raise LedgerError(
            f"`git {args[0]}` did not finish within {GIT_TIMEOUT}s while building the "
            "corpus repository; nothing was proven"
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise LedgerError(
            f"`git {args[0]}` failed while building the corpus repository "
            f"({(exc.stderr or '').strip().splitlines()[-1] if exc.stderr else exc}); "
            "nothing was proven"
        ) from exc


def head(repo):
    """The short object id of the commit just made, as a seed's `@commitNN` resolves to."""
    out = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
        timeout=GIT_TIMEOUT,
    )
    return out.stdout.strip()


def run_checkers(ledger, commit=None):
    """{checker: reports | Exception}"""
    produced = {}
    for name, fn in CHECKERS.items():
        try:
            reports = fn(ledger)
            for r in reports:
                r.commit = commit
            produced[name] = reports
        except Exception as exc:  # noqa: BLE001 — a crashing checker is a failing
            # checker, and the runner has to survive it to report which seed did it.
            produced[name] = exc
    return produced


def run_seed(seed, root):
    """(passed, lines, produced) for one seed directory."""
    expected = json.loads((seed / "expected.json").read_text(encoding="utf-8"))
    if not expected.get("expect"):
        # HIGH-45 put a floor under an empty corpus and a filter that matches no seed;
        # this is the same floor one level down. Without it, an `expect: []` seed prints
        # `1/1 seeds pass` over a seed that bound nothing to anything — a full pass for
        # zero evidence, which is the report this package exists to refuse. `test_corpus
        # .py`'s own `assert exp["expect"]` only holds the corpus this repository
        # currently ships; `run.py` is what an installed wheel runs, so the floor has to
        # live here too.
        return (
            False,
            ["expected.json declares no expectation rows; nothing was proven"],
            {name: [] for name in CHECKERS},
        )
    for r in expected["expect"]:
        if r.get("message") == "":
            # `matches()` reads an empty string as "no message was given" rather than as
            # a substring that matches every report, so a row written this way would
            # quietly bind as loosely as one that left the key out at all — the seed
            # author told nothing was wrong. Refused here instead, at the row that wrote
            # it, rather than left to surface later as a mismatch with no clear cause.
            raise ValueError(
                f"{seed.name}: a row's `message` is the empty string, which pins nothing; "
                'omit the key instead of writing ""'
            )
    rows = [
        (r["checker"], r["outcome"], *parse_where(r["where"]), r["why"], r.get("message"))
        for r in expected["expect"]
        if r["checker"] in CHECKERS and r["outcome"] in ("fail", "flag")
    ]
    produced = {name: [] for name in CHECKERS}
    crashes = []
    with tempfile.TemporaryDirectory(prefix="corpus-") as tmpdir:
        tmp = Path(tmpdir)
        if (seed / "commits").is_dir():
            git(tmp, "init", "-q")
            pins = {}
            for state in sorted(p for p in (seed / "commits").iterdir() if p.is_dir()):
                stage(state, tmp, pins)
                git(tmp, "add", "-A")
                git(tmp, "commit", "-qm", state.name)
                pins[state.name] = head(tmp)
                for name, result in run_checkers(
                    seed_ledger(root, tmp, repo=tmp), commit=state.name
                ).items():
                    if isinstance(result, Exception):
                        crashes.append((name, state.name, result))
                    else:
                        produced[name] += result
        else:
            stage(seed, tmp)
            for name, result in run_checkers(seed_ledger(root, tmp)).items():
                if isinstance(result, Exception):
                    crashes.append((name, None, result))
                else:
                    produced[name] += result

    lines = []
    for name, commit, exc in crashes:
        lines.append(
            f"{name} crashed{' at commit ' + commit if commit else ''}: "
            + "".join(traceback.format_exception(exc)).strip().splitlines()[-1]
        )
    for name in CHECKERS:
        mine = [r for r in rows if r[0] == name]
        reports = produced[name]
        for _, outcome, commit, entry, part, why, message in mine:
            hits = [r for r in reports if matches(r, commit, entry, part, message)]
            at_commit = f"commit {commit}, " if commit else ""
            at_entry = f"{entry} " if entry else ""
            place = f"{at_commit}{at_entry}{part}"
            wanted = [r for r in hits if r.outcome == outcome]
            if not wanted:
                got = "; ".join(f"{r.outcome} {r.message}" for r in hits) or "nothing there"
                lines.append(f"expected {name} {outcome} at {place} ({why}) — got {got}")
            elif len(wanted) > 1:
                # One row, one report. A place two rules both fail at is claimed by
                # whichever of them still exists, so the seed goes on passing when the
                # rule it was written for is deleted — coverage that is decoration.
                both = "; ".join(r.message for r in wanted)
                lines.append(
                    f"ambiguous {name} {outcome} at {place} ({why}) — "
                    f"{len(wanted)} reports satisfy one row: {both}"
                )
        for r in reports:
            if not any(
                matches(r, commit, entry, part, message) and r.outcome == outcome
                for _, outcome, commit, entry, part, _, message in mine
            ):
                prefix = f"commit {r.commit}, " if r.commit else ""
                lines.append(f"unexpected {name} {r.outcome} at {prefix}{r.place()}: {r.message}")
    return not lines, lines, produced


def main(argv=None):
    from ..cli import soften_output_encoding  # local: cli imports this module lazily

    soften_output_encoding()  # the `·` below is not encodable under an ASCII locale
    os.environ.setdefault("GIT_CONFIG_NOSYSTEM", "1")
    argv = list(sys.argv[1:] if argv is None else argv)
    verbose = "-v" in argv or "--verbose" in argv
    override = None
    if "--corpus" in argv:
        i = argv.index("--corpus")
        override = argv[i + 1]
        del argv[i : i + 2]
    names = [a for a in argv if not a.startswith("-")]
    root = corpus_root(override)
    seeds_dir = root / "seeds"
    if not seeds_dir.is_dir():
        print(f"no seeds under {seeds_dir}")
        return 1
    seeds = sorted(p for p in seeds_dir.iterdir() if p.is_dir())
    if names:
        unmatched = [n for n in names if not any(s.name.startswith(n) for s in seeds)]
        if unmatched:
            # `corpus D3` for the seed named `D03` used to print `0/0 seeds pass` and exit
            # 0: a green run over nothing, which is the report this package exists to
            # refuse.
            print(f"no seed under {seeds_dir} matches {', '.join(unmatched)}")
            return 1
        seeds = [s for s in seeds if any(s.name.startswith(n) for n in names)]
    if not seeds:
        # The release workflow proves the built wheel by running exactly this command, so
        # a wheel that shipped no seeds would otherwise pass the gate that exists to say
        # the checkers still work.
        print(f"no seeds under {seeds_dir}; nothing was proven")
        return 1
    passed = 0
    for seed in seeds:
        ok, lines, produced = run_seed(seed, root)
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'} {seed.name}")
        for ln in lines:
            print(f"   · {ln}")
        if verbose:
            for name, reports in produced.items():
                for r in reports:
                    prefix = f"commit {r.commit}, " if r.commit else ""
                    print(f"     {name}: {r.outcome} {prefix}{r.place()}: {r.message}")
    print(f"\n{passed}/{len(seeds)} seeds pass")
    return 0 if passed == len(seeds) else 1


if __name__ == "__main__":
    sys.exit(main())
