#!/usr/bin/env python3
"""Materialize the four templates as independent, checked Git repositories, and
demonstrate the one thing four single-threaded repositories cannot: two lines of work that
mint the same number, and the rewrite that repairs it before the merge."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
SPEC = json.loads((HERE / "portfolio.json").read_text(encoding="utf-8"))

SOURCES = {
    "ui-webapp": [
        (
            "backend-contract",
            "evidence/backend-openapi.yaml",
            "api",
            "Nimbus backend OpenAPI contract",
        ),
        (
            "research-summary",
            "evidence/research-summary.txt",
            "report",
            "Nimbus synthetic threshold study",
        ),
    ],
    "backend-service": [
        (
            "ui-contract",
            "evidence/ui-behavior-contract.txt",
            "contract",
            "Nimbus UI behavior contract",
        ),
        (
            "research-summary",
            "evidence/research-summary.txt",
            "report",
            "Nimbus synthetic threshold study",
        ),
    ],
    "research-repo": [
        (
            "latency-paper",
            "sources/latency-study.txt",
            "paper",
            "Synthetic latency study, Rao and Bell (2026)",
        ),
        (
            "review-consult",
            "sources/reviewer-consultation.txt",
            "consultation",
            "Synthetic review consultation",
        ),
    ],
    "documentation-repo": [
        (
            "ui-contract",
            "evidence/ui-behavior-contract.txt",
            "contract",
            "Nimbus UI behavior contract",
        ),
        (
            "backend-contract",
            "evidence/backend-openapi.yaml",
            "api",
            "Nimbus backend OpenAPI contract",
        ),
        (
            "research-summary",
            "evidence/research-summary.txt",
            "report",
            "Nimbus synthetic threshold study",
        ),
    ],
}


CONCURRENT_IDS = "concurrent-ids"
# The two claims the concurrent-authoring demonstration mints, one per line of work: the
# branch that states it, the slug, the section of the note it rests on, the assertion, and
# the metric its Scope names. Both are grounded in the same file and neither knows about
# the other, which is what makes the collision real rather than staged.
CONCURRENT_CLAIMS = (
    (
        "side",
        "latency-is-low",
        "Latency sweep",
        "The median review latency is 41 ms.",
        "median review latency",
    ),
    (
        "main",
        "errors-are-rare",
        "Error sweep",
        "The false-review rate is 3 percent.",
        "false-review rate",
    ),
)


def run(*args: str, cwd: Path, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.stdout


def ledger_env() -> dict[str, str]:
    env = os.environ.copy()
    src = str(PROJECT / "src")
    env["PYTHONPATH"] = src + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return env


def ledger(repo: Path, *args: str) -> str:
    return run(sys.executable, "-m", "claims_ledger", *args, cwd=repo, env=ledger_env())


def ledger_exiting(repo: Path, expected: int, *args: str) -> str:
    """Run a command that is supposed to refuse, and hold it to the refusal.

    `ledger` raises on any non-zero status, which is right for the four repositories: every
    command they run is supposed to succeed. Two of the commands here are supposed to fail
    — a dry run that writes nothing, and a merge the policy denies — and a demonstration
    that accepted either status would be showing nothing at all.
    """
    result = subprocess.run(
        (sys.executable, "-m", "claims_ledger", *args),
        cwd=repo,
        env=ledger_env(),
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != expected:
        raise RuntimeError(
            f"`claims-ledger {' '.join(args)}` exited {result.returncode}, "
            f"expected {expected}:\n{result.stdout}"
        )
    return result.stdout


def initialize(repo: Path) -> None:
    run("git", "init", "-q", cwd=repo)
    run("git", "config", "user.name", "Claims Ledger Example", cwd=repo)
    run("git", "config", "user.email", "examples@claims-ledger.invalid", cwd=repo)


def register_sources(name: str, repo: Path) -> None:
    for source_id, path, source_type, citation in SOURCES[name]:
        args = [
            "source",
            "add",
            path,
            "--id",
            source_id,
            "--type",
            source_type,
            "--citation",
            citation,
            "--retrieved",
            "2026-09-06",
            "--keep-path",
        ]
        if source_type == "paper":
            args.extend(("--authors", "Rao", "Bell"))
        if source_type == "consultation":
            args.extend(("--speaker", "reviewer"))
        ledger(repo, *args)


def materialize(destination: Path) -> list[Path]:
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"destination is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)

    repos = []
    held_entries: dict[str, dict[str, str]] = {}
    for name in SPEC["repositories"]:
        repo = destination / name
        shutil.copytree(HERE / "templates" / name, repo)
        entries_dir = repo / "ledger" / "entries"
        held_entries[name] = {
            path.name: path.read_text(encoding="utf-8") for path in sorted(entries_dir.glob("*.md"))
        }
        shutil.rmtree(entries_dir)
        repos.append(repo)

    for origin, snapshot in SPEC["snapshots"]:
        target = destination / snapshot
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(destination / origin, target)

    for name, repo in zip(SPEC["repositories"], repos, strict=True):
        initialize(repo)
        register_sources(name, repo)
        run("git", "add", ".", cwd=repo)
        run("git", "commit", "-q", "-m", "Add example artifacts and registered sources", cwd=repo)
        base = run("git", "rev-parse", "HEAD", cwd=repo).strip()

        entries_dir = repo / "ledger" / "entries"
        entries_dir.mkdir(parents=True)
        for filename, text in held_entries[name].items():
            (entries_dir / filename).write_text(text.replace("@BASE@", base), encoding="utf-8")
        entry_paths = [str(path.relative_to(repo)) for path in sorted(entries_dir.glob("*.md"))]
        ledger(repo, "sha", "--write", *entry_paths)
        run("git", "add", "ledger/entries", cwd=repo)
        run("git", "commit", "-q", "-m", "Add checked claims ledger", cwd=repo)
        ledger(repo, "hook", "--install")
        ledger(repo, "check")

    for origin, snapshot in SPEC["snapshots"]:
        if (destination / origin).read_bytes() != (destination / snapshot).read_bytes():
            raise RuntimeError(f"cross-repository snapshot differs: {snapshot} != {origin}")
    return repos


def fill_scaffold(path: Path, assertion: str, metric: str, section: str) -> None:
    """Fill a `new` scaffold the way a person would, and ground it by value.

    The anchor is left as `=?` for `sha --write` to fill with the digest of the section as
    the tree has it. That is the ground shape a rewrite can carry: a ground stated by
    reference into a commit the rewrite replaces loses the evidence it rests on, and costs
    a supersession rather than a re-read.
    """
    text = path.read_text(encoding="utf-8")
    text = text.replace("TODO: the claim, in this project's words. No quotation marks.", assertion)
    text = text.replace("metric: TODO", f"metric: {metric}")
    text = text.replace("cohort: TODO", "cohort: the demonstration cohort")
    text = text.replace("condition: TODO", "condition: the demonstration run, as recorded")
    text = re.sub(
        r"- TODO: one typed pointer[^\n]*\n",
        f'- lab: docs/observations.md \u00a7 "{section}" =?\n',
        text,
    )
    text = text.replace(
        "TODO: the rule by which the grounds support the assertion.",
        "The section records the reading the assertion states, and nothing wider.",
    )
    text = text.rstrip("\n") + "\n\n- docs/observations.md \u00b7 standing \u00b7 cites-as-live\n"
    path.write_text(text, encoding="utf-8")


def cite_in_section(note: Path, section: str, ident: str) -> None:
    """Write the citing sentence inside the section the entry pins, not beneath the file.

    This is also what gives the rewrite something to prove: the citation names the id, so
    moving the id changes the bytes of the very section the ground is anchored to, and the
    digest has to be re-pinned rather than left to go stale.
    """
    text = note.read_text(encoding="utf-8")
    heading = f"## {section}\n"
    start = text.index(heading) + len(heading)
    end = text.find("\n## ", start)
    end = len(text) if end == -1 else end
    body = text[start:end].rstrip("\n")
    sentence = f"\nStated as a claim here ({ident}, cites-as-live).\n"
    note.write_text(text[:start] + body + sentence + text[end:], encoding="utf-8")


def mint(
    repo: Path, slug: str, section: str, assertion: str, metric: str, ident: str | None
) -> str:
    """Mint one claim and leave the tree green. Returns the id it ended up with."""
    args = ["new", slug] + (["--id", ident] if ident else [])
    ledger(repo, *args)
    entry = next(iter(sorted((repo / "ledger" / "entries").glob(f"*-{slug}.md"))))
    full_id = entry.stem
    fill_scaffold(entry, assertion, metric, section)
    cite_in_section(repo / "docs" / "observations.md", section, full_id)
    ledger(repo, "sha", "--write", str(entry.relative_to(repo)))
    run("git", "add", "-A", cwd=repo)
    run("git", "commit", "-q", "-m", f"The {slug.replace('-', ' ')} claim", cwd=repo)
    return full_id


def demonstrate_concurrent_ids(destination: Path) -> tuple[Path, str, str]:
    """Two lines of work mint one number, and the branch is rewritten before it merges.

    The other four repositories cannot show this: it needs two lines of work, and they each
    have one. Kept out of `portfolio.json` for the same reason — it is not a fifth member of
    the product story, it is the one process this package has to get right when two sessions
    author at once.

    Returns the repository, the id that was minted twice, and the id it ended up under.
    """
    repo = destination / CONCURRENT_IDS
    shutil.copytree(HERE / "templates" / CONCURRENT_IDS, repo)
    initialize(repo)

    # `init` writes the configuration, the way a project that has never seen this
    # repository starts. The one key this demonstration is about is appended before either
    # branch exists: a configuration that changes on the branch is refused, because the
    # rewrite reads one configuration for every commit it replaces.
    ledger(repo, "init")
    config = repo / "claims-ledger.toml"
    text = config.read_text(encoding="utf-8").replace(
        'roster = "ROSTER.md"', '# roster = "ROSTER.md"'
    )
    config.write_text(text + '\nmerge-renumber = "refuse"\n', encoding="utf-8")
    run("git", "add", "-A", cwd=repo)
    run(
        "git",
        "commit",
        "-q",
        "-m",
        "The observations, and the ledger that answers for them",
        cwd=repo,
    )
    run("git", "branch", "-M", "main", cwd=repo)

    # The branch is cut here, after the base. Every ground the two entries state is anchored
    # by value, and the base itself is an ancestor of both branches, so nothing either entry
    # rests on lives inside the range the rewrite replaces.
    branch, slug, section, assertion, metric = CONCURRENT_CLAIMS[0]
    run("git", "checkout", "-q", "-b", branch, cwd=repo)
    moved = mint(repo, slug, section, assertion, metric, None)
    ledger(repo, "check")  # green on its own, which is the premise

    # The second line of work allocates the same number. `--id` is what makes that possible:
    # `new` with no id asks the whole repository, refs included, and would have stepped past
    # the number the branch is already holding.
    _, slug, section, assertion, metric = CONCURRENT_CLAIMS[1]
    run("git", "checkout", "-q", "main", cwd=repo)
    held = mint(repo, slug, section, assertion, metric, moved.split("-", 1)[0])
    ledger(repo, "check")  # green on its own too: nothing but the number is wrong

    # What the merge guard asks, from the receiving checkout. The policy is `refuse`, so it
    # denies the merge and names the repair rather than performing it.
    refusal = ledger_exiting(
        repo, 1, "renumber", "--onto", "main", "--branch", branch, "--on-merge"
    )
    # The refusal has to carry the repair, or an operator reading it learns only that they
    # are stuck. This is the sentence the merge guard hands back as its denial reason.
    repair = f"claims-ledger renumber --onto main --branch {branch} --write"
    if repair not in refusal:
        raise RuntimeError(f"the refusal does not name the repair `{repair}`:\n{refusal}")

    # The dry run, from the branch that moves: it prints the plan and writes nothing.
    run("git", "checkout", "-q", branch, cwd=repo)
    plan = ledger_exiting(repo, 1, "renumber", "--onto", "main")
    if "nothing was written" not in plan:
        raise RuntimeError(f"the dry run does not say it wrote nothing:\n{plan}")

    # The repair, asked from the receiving checkout the way an operator would after reading
    # the refusal. The branch that has not merged is the one that moves.
    run("git", "checkout", "-q", "main", cwd=repo)
    ledger(repo, "renumber", "--onto", "main", "--branch", branch, "--write")
    ledger_exiting(repo, 0, "renumber", "--onto", "main", "--branch", branch, "--on-merge")
    run("git", "merge", "-q", "--no-ff", "--no-edit", branch, cwd=repo)
    ledger(repo, "check")

    entries = sorted(path.stem for path in (repo / "ledger" / "entries").glob("*.md"))
    if len(entries) != 2 or len({name.split("-", 1)[0] for name in entries}) != 2:
        raise RuntimeError(f"the merged ledger does not carry two numbered entries: {entries}")
    if held not in entries or moved in entries:
        raise RuntimeError(f"the wrong side moved: {entries}")
    slug = moved.split("-", 1)[1]
    landed = next(name for name in entries if name.endswith(f"-{slug}"))
    return repo, moved, landed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, nargs="?")
    args = parser.parse_args(argv)
    temporary = None
    destination = args.destination
    if destination is None:
        temporary = tempfile.TemporaryDirectory(prefix="claims-ledger-portfolio-")
        destination = Path(temporary.name)
    try:
        repos = materialize(destination.resolve())
        for repo in repos:
            print(f"{repo.name}: check passed")
        snapshot_count = len(SPEC["snapshots"])
        print(
            f"portfolio: {len(repos)} repositories and {snapshot_count} "
            "cross-repository snapshots verified"
        )
        _, minted_twice, landed = demonstrate_concurrent_ids(destination)
        number = minted_twice.split("-", 1)[0]
        print(f"{CONCURRENT_IDS}: two lines of work each minted {number}; the merge was refused")
        print(f"{CONCURRENT_IDS}: {minted_twice} -> {landed}, rewritten before the merge")
        if temporary is None:
            print(f"wrote {destination.resolve()}")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"materialization failed: {exc}", file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError) and exc.stdout:
            print(exc.stdout, file=sys.stderr, end="")
        return 1
    finally:
        if temporary is not None:
            temporary.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
