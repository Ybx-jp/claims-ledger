"""QE6 — Part 2e: attack MEDIUM-35's `:(literal)` fix in both directions -- decoys must
not false-positive, real edits must still be caught -- for `:`, `*`, `?`, `[`, a path
that literally begins with `:(literal)`, a leading `-`, and a path outside the repo."""

import subprocess

from claims_ledger import freshness
from claims_ledger.schema import open_ledger


def _rev(project, *args):
    out = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", *args],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def outcomes(project):
    return [(r.outcome, r.part, r.message) for r in freshness.run(open_ledger(root=project.root))]


def build(project, target, pin=None):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts", "--allow-empty")
    pin = pin or _rev(project, "--short", "HEAD")
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working',
        f"- experiment: {target} @{pin}",
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    return path, pin


NOTE = "content v1\n"
NOTE2 = "content v2\n"


def test_colon_in_path(project):
    real = project.root / "docs"
    real.mkdir(exist_ok=True)
    (real / "a:b.md").write_text(NOTE, encoding="utf-8")
    build(project, "docs/a:b.md")
    (real / "a:b.md").write_text(NOTE2, encoding="utf-8")
    out = outcomes(project)
    print("COLON in path, real edit:", out)
    assert out and out[0][0] == "flag"


def test_question_mark_decoy(project):
    real = project.root / "docs"
    real.mkdir(exist_ok=True)
    (real / "a?b.md").write_text(NOTE, encoding="utf-8")
    (real / "aXb.md").write_text(NOTE, encoding="utf-8")  # matches `a?b.md` as a glob
    build(project, "docs/a?b.md")
    (real / "aXb.md").write_text(NOTE2, encoding="utf-8")  # edit only the decoy
    out = outcomes(project)
    print("? decoy (should be []):", out)
    assert out == []
    (real / "a?b.md").write_text(NOTE2, encoding="utf-8")  # edit the real file
    out2 = outcomes(project)
    print("? real edit (should flag):", out2)
    assert out2 and out2[0][0] == "flag"


def test_leading_dash_path(project):
    real = project.root
    (real / "-weird.md").write_text(NOTE, encoding="utf-8")
    build(project, "-weird.md")
    (real / "-weird.md").write_text(NOTE2, encoding="utf-8")
    out = outcomes(project)
    print("leading-dash path, real edit:", out)
    assert out and out[0][0] == "flag"


def test_path_that_is_literally_colon_literal_paren(project):
    # A filename that literally begins with the magic string `:(literal)` -- after the
    # code wraps it AGAIN as `:(literal):(literal)evil.md`, does git still find it?
    real = project.root
    weird_name = ":(literal)evil.md"
    try:
        (real / weird_name).write_text(NOTE, encoding="utf-8")
    except OSError as exc:
        print("SKIPPED -- filesystem rejects this filename:", exc)
        return
    build(project, weird_name)
    (real / weird_name).write_text(NOTE2, encoding="utf-8")
    out = outcomes(project)
    print(f"path literally starting with ':(literal)' -- {weird_name!r}, real edit:", out)


def test_path_outside_repo_traversal(project):
    # A target with `../` in it -- outside the repo root as a pathspec.
    build(project, "../outside.md")
    out = outcomes(project)
    print("path with ../ traversal, unedited:", out)


def test_star_decoy_and_real(project):
    real = project.root / "docs"
    real.mkdir(exist_ok=True)
    (real / "a*b.md").write_text(NOTE, encoding="utf-8")
    (real / "aZZb.md").write_text(NOTE, encoding="utf-8")  # matches a*b.md as a glob
    build(project, "docs/a*b.md")
    (real / "aZZb.md").write_text(NOTE2, encoding="utf-8")
    out = outcomes(project)
    print("* decoy (should be []):", out)
    assert out == []
    (real / "a*b.md").write_text(NOTE2, encoding="utf-8")
    out2 = outcomes(project)
    print("* real edit (should flag):", out2)
    assert out2 and out2[0][0] == "flag"
