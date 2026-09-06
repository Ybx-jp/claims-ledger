"""QE6 — count git subprocess invocations `freshness.run()` makes, to check whether
identical (pin, target) pairs across many grounds are memoized or re-asked every time."""

import subprocess

from claims_ledger import freshness
from claims_ledger.schema import open_ledger


def build_many_grounds(project, n, same_pin=True):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts")
    out = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    pin = out.stdout.strip()
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    grounds = "\n".join(f"- experiment: docs/note-001.md @{pin}" for _ in range(n))
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working', grounds
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    return path


def test_subprocess_calls_per_ground_same_pin(project, monkeypatch):
    n = 20
    build_many_grounds(project, n)
    calls = []
    real_run = subprocess.run

    def counting_run(*args, **kwargs):
        if args and isinstance(args[0], list) and args[0] and args[0][0] == "git":
            calls.append(args[0][1:])
        return real_run(*args, **kwargs)

    monkeypatch.setattr(subprocess, "run", counting_run)
    ledger = open_ledger(root=project.root)
    reports = freshness.run(ledger)
    print(f"{n} grounds, identical pin+target, unedited: {len(reports)} reports, "
          f"{len(calls)} git subprocess calls total ({len(calls)/n:.2f} per ground)")
    for c in calls[:10]:
        print("  ", c)
    print("  ... (truncated)" if len(calls) > 10 else "")
