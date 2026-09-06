"""QE6 — Part 2a: attack `is_object_name()` / MEDIUM-32 & LOW-36's fix. Every pin
now goes to git as a subprocess. Push on shape, ambiguity, cost, and injection-shaped
input. Print-only exploration; run with `pytest -s -q`."""

import shutil
import subprocess
import time

from claims_ledger import freshness
from claims_ledger.schema import open_ledger, git_call


def _rev(project, *args):
    out = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", *args],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def build(project, grounds, pin=None):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts", "--allow-empty")
    pin = pin or _rev(project, "--short", "HEAD")
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    lines = "\n".join("- " + g.format(pin=pin) for g in grounds)
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working', lines
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    return path, pin


def outcomes(project, write=False, cached=False):
    return [
        (r.outcome, r.part, r.message)
        for r in freshness.run(open_ledger(root=project.root), write=write, cached=cached)
    ]


# ---- leading-dash pin: argv injection into git rev-parse -------------------------------

def test_dash_pin_argv_injection(project):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts")
    art = project.root / "docs" / "note-001.md"
    for evil_pin in ["--git-dir=/etc", "-h", "--upload-pack=x", "--", "---"]:
        r1 = git_call(project.root, "rev-parse", "--symbolic-full-name", evil_pin)
        r2 = git_call(project.root, "rev-parse", "--verify", "--quiet", evil_pin)
        print(f"pin={evil_pin!r}: symbolic-full-name ok={r1.ok} out={r1.out!r} why={r1.why!r}"
              f" | verify ok={r2.ok} code={r2.code} out={r2.out!r}")


def test_dash_pin_through_ground(project):
    # A ground literally pinned at a string beginning with `-`.
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts")
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working',
        "- experiment: docs/note-001.md @--upload-pack=x",
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    out = outcomes(project)
    print("DASH PIN GROUND freshness:", out)


# ---- empty string pin -------------------------------------------------------------------

def test_empty_pin(project):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts")
    r1 = git_call(project.root, "rev-parse", "--symbolic-full-name", "")
    r2 = git_call(project.root, "rev-parse", "--verify", "--quiet", "")
    print(f"empty pin: symbolic ok={r1.ok} out={r1.out!r} | verify ok={r2.ok} code={r2.code}")


# ---- abbreviated 7-char object id --------------------------------------------------------

def test_abbreviated_object_id(project):
    art = project.root / "docs" / "note-001.md"
    path, pin = build(project, ["experiment: docs/note-001.md @{pin}"])  # pin is --short (7ish)
    print("abbreviated pin used:", pin, "len:", len(pin))
    out = outcomes(project)
    print("ABBREV before edit:", out)
    art.write_text("edited\n", encoding="utf-8")
    print("ABBREV after edit:", outcomes(project))


# ---- ref/object-id collision: a branch literally named as a full hex sha ---------------

def test_ref_object_collision(project):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts")
    full = _rev(project, "HEAD")
    # Create a branch whose name IS a valid full hex object id (different commit).
    project.git("branch", full)
    r1 = git_call(project.root, "rev-parse", "--symbolic-full-name", full)
    r2 = git_call(project.root, "rev-parse", "--verify", "--quiet", full)
    print(f"COLLISION pin={full}: symbolic ok={r1.ok} out={r1.out!r} | verify ok={r2.ok} out={r2.out!r}")
    # Now use this as a ground pin and see what freshness makes of it.
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working',
        f"- experiment: docs/note-001.md @{full}",
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    out = outcomes(project)
    print("COLLISION ground freshness:", out)


# ---- git missing from PATH ---------------------------------------------------------------

def test_git_missing(project, monkeypatch):
    art = project.root / "docs" / "note-001.md"
    path, pin = build(project, ["experiment: docs/note-001.md @{pin}"])
    art.write_text("edited\n", encoding="utf-8")
    real_which = shutil.which

    def fake_which(name):
        return None if name == "git" else real_which(name)

    monkeypatch.setattr(shutil, "which", fake_which)
    out = outcomes(project)
    print("GIT MISSING freshness:", out)
    assert out and out[0][0] == "fail"


# ---- performance: N grounds at the SAME pin, subprocess calls per ground ---------------

def test_perf_many_grounds_same_pin(project):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts")
    pin = _rev(project, "--short", "HEAD")
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    n = 100
    grounds = "\n".join(f"- experiment: docs/note-001.md @{pin}" for _ in range(n))
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working', grounds
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    t0 = time.time()
    out = outcomes(project)
    dt = time.time() - t0
    print(f"PERF: {n} grounds, same pin, freshness.run() took {dt:.3f}s ({dt/n*1000:.2f}ms/ground)")
