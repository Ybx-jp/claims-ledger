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

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

from .. import propagate, references, resolve, validate
from ..config import Config
from ..schema import Ledger

CORPUS = Path(__file__).resolve().parent

CHECKERS = {
    "validate": lambda ledger: validate.run(ledger),
    "resolve": lambda ledger: resolve.run(ledger),
    "references": lambda ledger: references.run(ledger),
    "propagate": lambda ledger: propagate.run(ledger, write=False),
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
    commit, rest = m.group(1), m.group(2).strip()
    em = ENTRY_RE.match(rest)
    if em:
        return commit, em.group(1), em.group(2).strip()
    return commit, None, rest


def matches(report, commit, entry, part):
    if report.commit != commit or report.entry != entry:
        return False
    rp, qp = report.part.casefold(), part.casefold()
    return rp == qp or rp.startswith(qp + " ")


def seed_ledger(root, staged, repo=None):
    docs = sorted((staged / "docs").glob("*.md")) if (staged / "docs").is_dir() else []
    return Ledger(
        config=corpus_config(root, staged / "entries"),
        docs=[(f"docs/{p.name}", p) for p in docs],
        repo=repo,
    )


def stage(src, dst):
    for name in ("entries", "docs"):
        if (dst / name).exists():
            shutil.rmtree(dst / name)
        if (src / name).is_dir():
            shutil.copytree(src / name, dst / name)


def git(repo, *args):
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
    )


def run_checkers(ledger, commit=None):
    """{checker: reports | Exception}"""
    produced = {}
    for name, fn in CHECKERS.items():
        try:
            reports = fn(ledger)
            for r in reports:
                r.commit = commit
            produced[name] = reports
        except Exception as exc:  # a crashing checker is a failing checker
            produced[name] = exc
    return produced


def run_seed(seed, root):
    """(passed, lines, produced) for one seed directory."""
    expected = json.loads((seed / "expected.json").read_text(encoding="utf-8"))
    rows = [
        (r["checker"], r["outcome"], *parse_where(r["where"]), r["why"])
        for r in expected["expect"]
        if r["checker"] in CHECKERS and r["outcome"] in ("fail", "flag")
    ]
    produced = {name: [] for name in CHECKERS}
    crashes = []
    with tempfile.TemporaryDirectory(prefix="corpus-") as tmp:
        tmp = Path(tmp)
        if (seed / "commits").is_dir():
            git(tmp, "init", "-q")
            for state in sorted(p for p in (seed / "commits").iterdir() if p.is_dir()):
                stage(state, tmp)
                git(tmp, "add", "-A")
                git(tmp, "commit", "-qm", state.name)
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
        for _, outcome, commit, entry, part, why in mine:
            hits = [r for r in reports if matches(r, commit, entry, part)]
            if not any(r.outcome == outcome for r in hits):
                got = "; ".join(f"{r.outcome} {r.message}" for r in hits) or "nothing there"
                place = f"{'commit ' + commit + ', ' if commit else ''}{entry + ' ' if entry else ''}{part}"
                lines.append(f"expected {name} {outcome} at {place} ({why}) — got {got}")
        for r in reports:
            if not any(
                matches(r, commit, entry, part) and r.outcome == outcome
                for _, outcome, commit, entry, part, _ in mine
            ):
                prefix = f"commit {r.commit}, " if r.commit else ""
                lines.append(f"unexpected {name} {r.outcome} at {prefix}{r.place()}: {r.message}")
    return not lines, lines, produced


def main(argv=None):
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
        seeds = [s for s in seeds if any(s.name.startswith(n) for n in names)]
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
