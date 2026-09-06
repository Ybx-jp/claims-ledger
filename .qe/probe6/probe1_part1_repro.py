"""QE6 — Part 1: reproduce each of the ten findings by hand against the fixed tip
(776500b) and record the observed behaviour. Print-only; run with `pytest -s -q`."""

import subprocess

from claims_ledger import freshness, resolve, validate
from claims_ledger.schema import exit_code, open_ledger

NOTE = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.
"""


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


# ---- HIGH-29: section is part of discharge identity -----------------------------------

def test_high29_section_identity(project):
    note1 = project.root / "docs" / "note-001.md"
    note1.write_text(NOTE + "\n## Method\n\nAggregation over one layer.\n", encoding="utf-8")
    path, pin = build(project, [
        'lab: docs/note-001.md § "Observation" @{pin}',
        'lab: docs/note-001.md § "Method" @{pin}',
    ])
    note1.write_text(
        NOTE.replace("0.04", "0.09") + "\n## Method\n\nAggregation over two layers.\n",
        encoding="utf-8",
    )
    before = outcomes(project)
    print("HIGH-29 before discharge:", before)
    assert {o[0] for o in before} == {"flag"} and len(before) == 2
    # Manually append a verdict naming only Observation, as F-1's repro does.
    text = path.read_text(encoding="utf-8")
    head, marker, tail = text.partition("\n## References")
    block = (
        "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
        '  evidence: lab: docs/note-001.md § "Observation" @{pin}\n'
        "  note: propagated from a moved ground\n"
    ).format(pin=pin)
    path.write_text(head.rstrip("\n") + "\n\n" + block + marker + tail, encoding="utf-8")
    after = outcomes(project)
    print("HIGH-29 after discharging only Observation:", after)
    assert len(after) == 1 and "Method" in after[0][2] and after[0][0] == "flag"
    print("HIGH-29: FIXED — second ground (Method) still flags after Observation discharged")


# ---- HIGH-30: --write exit code over `moved` -------------------------------------------

def test_high30_write_exit_code_moved(project):
    art = project.root / "docs" / "note-001.md"
    build(project, ["experiment: docs/note-001.md @{pin}"])
    art.write_text(NOTE.replace("0.04", "0.09"), encoding="utf-8")
    reports = freshness.run(open_ledger(root=project.root), write=True)
    code = exit_code(reports)
    print("HIGH-30 outcomes:", [(r.outcome, r.message) for r in reports], "exit:", code)
    assert code != 0
    print("HIGH-30: FIXED — moved+write now exits non-zero")


# ---- HIGH-31: nested subsection --------------------------------------------------------

def test_high31_nested_subsection(project):
    art = project.root / "docs" / "note-001.md"
    art.write_text(
        "# note 001\n\n## Observation\n\n### Detail\n\nerr=0.04\n\n## Method\n\nmean agg\n",
        encoding="utf-8",
    )
    build(project, ['lab: docs/note-001.md § "Observation" @{pin}'])
    art.write_text(
        "# note 001\n\n## Observation\n\n### Detail\n\nerr=0.99 (INVERTED)\n\n## Method\n\nmean agg\n",
        encoding="utf-8",
    )
    out = outcomes(project)
    res = [(r.outcome, r.message) for r in resolve.run(open_ledger(root=project.root))]
    print("HIGH-31 freshness:", out)
    print("HIGH-31 resolve:", res)
    assert out and out[0][0] == "flag" and "moved" in out[0][2]
    print("HIGH-31: FIXED — edit under ### Detail now flags § Observation as moved")


# ---- MEDIUM-32: uppercase object id ----------------------------------------------------

def test_medium32_uppercase_pin(project):
    # build a repo and use HEAD's full hex, uppercased, as the pin
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts", "--allow-empty")
    full = _rev(project, "HEAD").upper()
    art = project.root / "docs" / "note-001.md"
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
    print("MEDIUM-32 uppercase pin, unedited:", out)
    assert out == []
    art.write_text(NOTE.replace("0.04", "0.09"), encoding="utf-8")
    out2 = outcomes(project)
    print("MEDIUM-32 uppercase pin, after edit:", out2)
    assert out2 and out2[0][0] == "flag" and "moved" in out2[0][2]
    print("MEDIUM-32: FIXED — uppercase pin compared, not treated as unstable")


# ---- MEDIUM-33: --cached ------------------------------------------------------------------

def test_medium33_cached_staged_edit_reverted_worktree(project):
    art = project.root / "docs" / "note-001.md"
    build(project, ["experiment: docs/note-001.md @{pin}"])
    original = art.read_text(encoding="utf-8")
    art.write_text(NOTE.replace("0.04", "0.09"), encoding="utf-8")
    project.git("add", "docs/note-001.md")
    art.write_text(original, encoding="utf-8")  # revert working tree, keep index staged
    staged = subprocess.run(
        ["git", "-C", str(project.root), "diff", "--cached", "--name-only"],
        capture_output=True, text=True,
    ).stdout
    print("staged files:", staged.strip())
    out_cached = outcomes(project, cached=True)
    out_worktree = outcomes(project, cached=False)
    print("MEDIUM-33 --cached:", out_cached)
    print("MEDIUM-33 no --cached:", out_worktree)
    assert out_cached and out_cached[0][0] == "flag"
    assert out_worktree == []
    cli_code = project.cl("check", "--cached")
    print("MEDIUM-33 CLI check --cached exit:", cli_code)


# ---- MEDIUM-34: revert wedge ------------------------------------------------------------

def test_medium34_revert_no_wedge(project):
    art = project.root / "docs" / "note-001.md"
    build(project, ["experiment: docs/note-001.md @{pin}"])
    art.write_text(NOTE.replace("0.04", "0.09"), encoding="utf-8")
    freshness.run(open_ledger(root=project.root), write=True)
    project.git("add", "-A")
    project.git("commit", "-qm", "remeasure and discharge")
    art.write_text(NOTE, encoding="utf-8")  # revert
    project.git("add", "-A")
    project.git("commit", "-qm", "revert to original")
    out = outcomes(project)
    print("MEDIUM-34 after revert-after-discharge:", out)
    assert out == []
    print("MEDIUM-34: FIXED — reverted drift no longer wedges the ledger")


# ---- MEDIUM-35: pathspec glob decoy ------------------------------------------------------

def test_medium35_glob_decoy(project):
    (project.root / "docs" / "note[1].md").write_text(NOTE, encoding="utf-8")
    (project.root / "docs" / "note1.md").write_text(NOTE, encoding="utf-8")
    build(project, ["experiment: docs/note[1].md @{pin}"])
    (project.root / "docs" / "note1.md").write_text(NOTE.replace("0.04", "0.09"), "utf-8")
    out_decoy = outcomes(project)
    print("MEDIUM-35 decoy edited (should be []):", out_decoy)
    assert out_decoy == []
    (project.root / "docs" / "note[1].md").write_text(NOTE.replace("0.04", "0.09"), "utf-8")
    out_real = outcomes(project)
    print("MEDIUM-35 real edited (should flag):", out_real)
    assert out_real and out_real[0][0] == "flag"
    print("MEDIUM-35: FIXED — decoy no false positive, true positive still fires")


# ---- LOW-36: non-hex pin naming nothing --------------------------------------------------

def test_low36_nonexistent_named_pin(project):
    build(project, ["experiment: docs/note-001.md @v9.9"], pin="v9.9")
    out = outcomes(project)
    res = [(r.outcome, r.message) for r in resolve.run(open_ledger(root=project.root))]
    print("LOW-36 freshness:", out)
    print("LOW-36 resolve:", res)
    assert out == []  # freshness silent
    assert res and res[0][0] == "fail"
    print("LOW-36: FIXED — freshness silent, only resolve reports it, once")


# ---- LOW-37: spec moved to say `git diff` not hash-object --------------------------------

def test_low37_spec_says_git_diff(project):
    import pathlib
    spec = pathlib.Path("/tmp/qe6-fresh/docs/FRESHNESS.md").read_text(encoding="utf-8")
    # step 4 of "The comparison, exactly" must now say git diff, not hash-object, as the
    # primary method (hash-object is still mentioned in the "Built —" explanation of why
    # the spec changed, which is fine).
    step4 = spec.split("4. `git diff")[1] if "4. `git diff" in spec else ""
    assert "4. `git diff --name-only" in spec
    print("LOW-37: SPEC MOVED — spec's step 4 now documents git diff comparison with rationale")


# ---- LOW-38: verbatim messages -----------------------------------------------------------

def test_low38_messages_match_spec(project):
    import pathlib
    spec = pathlib.Path("/tmp/qe6-fresh/docs/FRESHNESS.md").read_text(encoding="utf-8")
    art = project.root / "docs" / "note-001.md"
    build(project, ["experiment: docs/note-001.md @{pin}"])
    art.write_text(NOTE.replace("0.04", "0.09"), encoding="utf-8")
    out = outcomes(project)
    msg = out[0][2]
    print("LOW-38 code message:", msg)
    assert "has moved:" in msg
    assert "has moved:" in spec
    print("LOW-38: FIXED — spec verbatim examples match code output")
