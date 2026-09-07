#!/usr/bin/env python3
"""Reproduce the films' scenarios in fresh materializations of the example
portfolio and write every surface they show, verbatim, to src/captures.ts.

    python3 tools/capture.py

Two scenarios, one per film. `refuted`: a new measured claim R0013 is written;
a refuted verdict on R0001 cites it as evidence; check fails on everything
that cited R0001 live; propagate writes the dependents their row; the hook
refuses the commit. `superseded`: a new claim R0013 declares supersedes:
R0006 and keeps its Scope; a superseded verdict on R0006 names it; check is
clean both ways; the hook accepts the commit.

The films draw nothing they invent: the entries, the rows, each command's
output and the hook's answer are the bytes this script captured, and the
module records when, from which claims-ledger commit, and how.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
PROJECT = HERE.parent.parent  # the claims-ledger checkout
APPEND = "<!-- APPEND BELOW THIS LINE ONLY -->"


def sh(args: list[str], cwd: Path) -> tuple[int, str]:
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    return p.returncode, (p.stdout + p.stderr).rstrip("\n")


def pinned_commit(text: str) -> str:
    return next(tok for tok in text.split() if tok.startswith("@") and len(tok) == 41)


REFUTED = {
    "entry": "R0001-threshold-balances-review-errors",
    "dependent": "R0003-threshold-generalizes",
    "new": "R0013-pilot-b-miss-rate-exceeds-margin",
    "newText": """---
id: R0013-pilot-b-miss-rate-exceeds-margin
kind: claim
stated: 2026-09-07T09:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0
---

## Assertion

In pilot-b, the 0.72 threshold puts the miss rate at 0.09, above the 0.05 that pilot-a
recorded.

## Scope

metric: miss rate
cohort: synthetic pilot-b rows
condition: threshold fixed at 0.72, scoring model and review policy held fixed

## Grounds

- experiment: experiments/threshold.csv {commit}

## Warrant

The rerun row records the pilot-b miss rate directly; it exceeds the pilot-a figure the
earlier claim rests on.

## Backing

none

{append}

## Verdicts


## References

""",
    "verdict": (
        "- 2026-09-07T09:05:00-07:00 · refuted · grade: measured · author: main\n"
        "  evidence: entry: R0013-pilot-b-miss-rate-exceeds-margin · cites-as-live\n"
        "  note: pilot-b does not hold the miss-rate margin\n"
    ),
    "propagate": True,
    "commitMessage": "refute R0001",
}

SUPERSEDED = {
    "entry": "R0006-threshold-displays-as-seventy-two-percent",
    "dependent": None,
    "new": "R0013-threshold-displays-as-seventy-two-percent-everywhere",
    "newText": """---
id: R0013-threshold-displays-as-seventy-two-percent-everywhere
kind: claim
stated: 2026-09-07T09:00:00-07:00
author: main
grade: measured
supersedes: R0006-threshold-displays-as-seventy-two-percent
verbatim_sha: 0
---

## Assertion

The selected demonstration threshold displays as 72 percent on every surface that shows
it, not only the console banner.

## Scope

metric: threshold rounded to one decimal place
cohort: synthetic pilot-a selected row
condition: ordinary half-up decimal presentation

## Grounds

- experiment: experiments/threshold.csv {commit}

## Warrant

The same selected row records 0.72; the predecessor named one surface, and the display
rule is the same on all of them.

## Backing

none

{append}

## Verdicts


## References

""",
    "verdict": (
        "- 2026-09-07T09:05:00-07:00 · superseded · grade: measured · author: main\n"
        "  evidence: entry: R0013-threshold-displays-as-seventy-two-percent-everywhere"
        " · supersedes\n"
        "  note: replaced by the claim about every surface\n"
    ),
    "propagate": False,
    "commitMessage": "supersede R0006",
}


def run_scenario(spec: dict[str, object]) -> dict[str, object]:
    work = Path(tempfile.mkdtemp(prefix="claims-ledger-film-"))
    dest = work / "portfolio"
    materialize = [
        "uv", "run", "--project", str(PROJECT),
        "python", str(PROJECT / "examples" / "materialize.py"), str(dest),
    ]  # fmt: skip
    rc, out = sh(materialize, PROJECT)
    if rc != 0:
        print(out, file=sys.stderr)
        raise SystemExit(rc)
    repo = dest / "research-repo"
    cl = ["uv", "run", "--project", str(PROJECT), "claims-ledger"]

    def run(*args: str) -> dict[str, object]:
        code, text = sh([*cl, *args], repo)
        return {"argv": ["claims-ledger", *args], "exit": code, "text": text}

    entry_path = repo / "ledger" / "entries" / f"{spec['entry']}.md"
    entry_before = entry_path.read_text(encoding="utf-8")
    commit = pinned_commit(entry_before)

    status_before = run("status")
    check_before = run("check")

    # A new claim is written, and fingerprinted the way an author would.
    new_rel = f"ledger/entries/{spec['new']}.md"
    new_path = repo / new_rel
    new_path.write_text(str(spec["newText"]).format(commit=commit, append=APPEND), encoding="utf-8")
    sha = run("sha", "--write", new_rel)
    new_text = new_path.read_text(encoding="utf-8")

    # The verdict on the old claim names the new one.
    row = str(spec["verdict"])
    assert entry_before.count("## Verdicts\n\n") == 1
    entry_after = entry_before.replace("## Verdicts\n\n", "## Verdicts\n\n" + row + "\n", 1)
    entry_path.write_text(entry_after, encoding="utf-8")

    status_after_verdict = run("status")
    check_after_verdict = run("check")
    propagate = run("propagate", "--write") if spec["propagate"] else None
    dependent_after = (
        (repo / "ledger" / "entries" / f"{spec['dependent']}.md").read_text(encoding="utf-8")
        if spec["dependent"]
        else None
    )
    status_after_propagate = run("status") if spec["propagate"] else None

    sh(["git", "add", "-A"], repo)
    hook_code, hook_text = sh(["git", "commit", "-q", "-m", str(spec["commitMessage"])], repo)
    _, head_after = sh(["git", "log", "--oneline", "-1"], repo)
    shutil.rmtree(work, ignore_errors=True)
    return {
        "entryId": spec["entry"],
        "entryPath": f"ledger/entries/{spec['entry']}.md",
        "entryBefore": entry_before,
        "entryAfter": entry_after,
        "verdictRow": row,
        "newId": spec["new"],
        "newPath": new_rel,
        "newText": new_text,
        "sha": sha,
        "dependentId": spec["dependent"],
        "dependentPath": f"ledger/entries/{spec['dependent']}.md" if spec["dependent"] else None,
        "dependentAfter": dependent_after,
        "statusBefore": status_before,
        "checkBefore": check_before,
        "statusAfterVerdict": status_after_verdict,
        "checkAfterVerdict": check_after_verdict,
        "propagate": propagate,
        "statusAfterPropagate": status_after_propagate,
        "commit": {
            "argv": ["git", "commit", "-m", str(spec["commitMessage"])],
            "exit": hook_code,
            "text": hook_text,
        },
        "headAfterCommit": head_after,
        "pinnedCommit": commit,
    }


def main() -> int:
    _, cl_commit = sh(["git", "rev-parse", "--short", "HEAD"], PROJECT)
    cl = ["uv", "run", "--project", str(PROJECT), "claims-ledger"]
    _, version = sh([*cl, "--version"], PROJECT)
    captures = {
        "provenance": {
            "capturedAt": datetime.now(UTC).isoformat(timespec="seconds"),
            "claimsLedgerCommit": cl_commit,
            "claimsLedgerVersion": version,
            "materializedWith": "examples/materialize.py",
            "repository": "research-repo",
            "how": (
                "per scenario, in a fresh materialization: status; check; write the new entry and "
                "`sha --write` it; append the verdict to the old entry by hand; status; check; "
                "propagate --write and status (refuted only); git add -A; git commit "
                "(the installed hook runs)"
            ),
        },
        "refuted": run_scenario(REFUTED),
        "superseded": run_scenario(SUPERSEDED),
    }
    body = json.dumps(captures, indent=2, ensure_ascii=False)
    (HERE / "src" / "captures.ts").write_text(
        "// GENERATED by tools/capture.py — verbatim surfaces from fresh materializations of\n"
        "// examples/. Do not edit; re-run the script.\n"
        f"export const CAPTURES = {body} as const;\n",
        encoding="utf-8",
    )
    for name in ("refuted", "superseded"):
        c = captures[name]
        check_exit = c["checkAfterVerdict"]["exit"]
        commit_exit = c["commit"]["exit"]
        print(
            f"{name}: check exit {check_exit} · commit exit {commit_exit} · {c['headAfterCommit']}"
        )
    return 0


if __name__ == "__main__":
    os.environ.setdefault("GIT_TERMINAL_PROMPT", "0")
    sys.exit(main())
