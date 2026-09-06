"""QE6 — Part 2c: MEDIUM-33 says the surface that matters most is "the installed
pre-commit hook, where HIGH-24 lived." Does the ACTUAL installed hook now pass
`--cached` to `freshness`? `cli.HOOK_TEMPLATE` is read directly below, and then the
installed hook script is run for real, the way git would run it, over an ordinary
partial-staging scenario (edit the pinned artifact, `git add` it, put the working-tree
copy back)."""

import subprocess

from claims_ledger.cli import HOOK_TEMPLATE, hook_text


def test_hook_template_freshness_line():
    print("HOOK_TEMPLATE:\n" + HOOK_TEMPLATE)
    lines = [ln for ln in HOOK_TEMPLATE.splitlines() if "freshness" in ln]
    print("freshness line(s) in the hook template:", lines)
    for ln in lines:
        if "--cached" not in ln:
            print(f"CONFIRMED: hook invokes freshness WITHOUT --cached: {ln!r}")


def test_installed_hook_misses_a_staged_drift(project):
    art = project.root / "docs" / "note-001.md"
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
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working',
        f"- experiment: docs/note-001.md @{pin}",
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")

    assert project.cl("hook", "--install") == 0
    hook_path = project.root / ".git" / "hooks" / "pre-commit"
    assert hook_path.exists()

    # Ordinary partial staging: edit the pinned artifact, stage it, then revert the
    # working-tree copy (e.g. the author staged a fix, then reverted their local edit by
    # hand while ANOTHER change is what's really about to be committed).
    original = art.read_text(encoding="utf-8")
    art.write_text(original.replace("0.04", "0.09"), encoding="utf-8")
    project.git("add", "docs/note-001.md")
    art.write_text(original, encoding="utf-8")

    result = subprocess.run(
        [str(hook_path)],
        cwd=str(project.root),
        capture_output=True,
        text=True,
    )
    print("INSTALLED HOOK exit code:", result.returncode)
    print("INSTALLED HOOK stdout:\n", result.stdout)
    print("INSTALLED HOOK stderr:\n", result.stderr)
    if result.returncode == 0:
        print(
            "CONFIRMED: the installed pre-commit hook exits 0 over a staged drift it "
            "never looked at, because its `freshness` line has no --cached — the exact "
            "MEDIUM-33 scenario, still live in the one place the finding named as the "
            "surface that matters most."
        )
