#!/usr/bin/env python3
"""Materialize the four templates as independent, checked Git repositories."""

from __future__ import annotations

import argparse
import json
import os
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
