"""Fifth-pass freshspec probes. Print-only exploration; the regressions live in
tests/test_freshness_spec.py."""

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
        capture_output=True,
        text=True,
        check=True,
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


def outcomes(project, write=False):
    return [
        (r.outcome, r.part, r.message)
        for r in freshness.run(open_ledger(root=project.root), write=write)
    ]


def append(path, block):
    text = path.read_text(encoding="utf-8")
    head, marker, tail = text.partition("\n## References")
    path.write_text(head.rstrip("\n") + "\n\n" + block + marker + tail, encoding="utf-8")


def contested(pointer_line, note="propagated from a moved ground"):
    return (
        "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
        f"  evidence: {pointer_line}\n"
        f"  note: {note}\n"
    )


# --- A. glob metacharacters in an artifact path ---------------------------------------


def test_a_glob_path(project):
    (project.root / "docs" / "note[1].md").write_text(NOTE, encoding="utf-8")
    build(project, ["experiment: docs/note[1].md @{pin}"])
    print("FRESH BEFORE:", outcomes(project))
    (project.root / "docs" / "note[1].md").write_text(
        NOTE.replace("0.04", "0.09"), encoding="utf-8"
    )
    print("AFTER EDITING THE REAL FILE:", outcomes(project))
    print("RESOLVE:", [r.message for r in resolve.run(open_ledger(root=project.root))])
    print("CLI:", project.cl("freshness"))


def test_a2_star_path(project):
    (project.root / "docs" / "a*b.md").write_text(NOTE, encoding="utf-8")
    build(project, ["experiment: docs/a*b.md @{pin}"])
    (project.root / "docs" / "a*b.md").write_text(NOTE.replace("0.04", "0.09"), encoding="utf-8")
    print("STAR EDITED:", outcomes(project))


# --- B. --cached ----------------------------------------------------------------------


def test_b_cached_ignored(project):
    build(project, ["experiment: docs/note-001.md @{pin}"])
    # The artifact is removed from the index; the commit being made drops the ground.
    project.git("rm", "-q", "--cached", "docs/note-001.md")
    print("STAGED DELETION, freshness:", outcomes(project))
    print("check --cached exit:", project.cl("check", "--cached"))


def test_b2_cached_unstaged_edit(project):
    build(project, ["experiment: docs/note-001.md @{pin}"])
    (project.root / "docs" / "note-001.md").write_text(
        NOTE.replace("0.04", "0.09"), encoding="utf-8"
    )
    print("UNSTAGED EDIT under --cached:", project.cl("check", "--cached"))


# --- C. has_acknowledged ignores the section ------------------------------------------


def test_c_section_blind_discharge(project):
    two = NOTE + "\n## Method\n\nStar graphs, one layer, sixteen dimensions.\n"
    (project.root / "docs" / "note-001.md").write_text(two, encoding="utf-8")
    path, pin = build(
        project,
        [
            'lab: docs/note-001.md § "Observation" @{pin}',
            'lab: docs/note-001.md § "Method" @{pin}',
        ],
    )
    (project.root / "docs" / "note-001.md").write_text(
        two.replace("0.04", "0.09").replace("sixteen", "thirty-two"), encoding="utf-8"
    )
    print("BOTH DRIFTED:", outcomes(project))
    append(path, contested(f'lab: docs/note-001.md § "Observation" @{pin}'))
    print("ONE VERDICT:", outcomes(project))
    print("VALIDATE:", [r.message for r in validate.run(open_ledger(root=project.root))])


# --- D. --write exit code over a moved ground -----------------------------------------


def test_d_write_exit_code(project):
    path, _ = build(project, ["experiment: docs/note-001.md @{pin}"])
    (project.root / "docs" / "note-001.md").write_text(
        NOTE.replace("0.04", "0.09"), encoding="utf-8"
    )
    reports = freshness.run(open_ledger(root=project.root), write=True)
    print("REPORTS:", [(r.outcome, r.message) for r in reports])
    print("EXIT:", exit_code(reports))
    print("WROTE:", path.read_text(encoding="utf-8").count("author: propagation"))


def test_d2_cli_write_exit(project):
    build(project, ["experiment: docs/note-001.md @{pin}"])
    (project.root / "docs" / "note-001.md").write_text(
        NOTE.replace("0.04", "0.09"), encoding="utf-8"
    )
    print("CLI freshness --write exit:", project.cl("freshness", "--write"))


# --- E. a nested subsection ends the section (default markdown pattern) ---------------


def test_e_nested_subsection(project):
    nested = """# note 001

## Observation

At a stale fraction of 0.1 the measured error was 0.04.

### Detail

The sweep ran sixteen times.

## Method

Star graphs.
"""
    (project.root / "docs" / "note-001.md").write_text(nested, encoding="utf-8")
    build(project, ['lab: docs/note-001.md § "Observation" @{pin}'])
    (project.root / "docs" / "note-001.md").write_text(
        nested.replace("sixteen times", "twice, and the result inverted"), encoding="utf-8"
    )
    print("EDIT UNDER THE SUBHEADING:", outcomes(project))
    print("RESOLVE:", [r.message for r in resolve.run(open_ledger(root=project.root))])


# --- F. a section that is not at the pin ----------------------------------------------


def test_f_section_absent_at_pin(project):
    # The pin predates the section: the file at the pin has no `## Observation`.
    (project.root / "docs" / "note-001.md").write_text("# note 001\n\nnothing yet.\n", "utf-8")
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "before the section")
    pin = _rev(project, "--short", "HEAD")
    (project.root / "docs" / "note-001.md").write_text(NOTE, encoding="utf-8")
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    path.write_text(
        path.read_text(encoding="utf-8").replace("@working", f"@{pin}"), encoding="utf-8"
    )
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    print("FRESHNESS:", outcomes(project))
    print("RESOLVE:", [(r.outcome, r.message) for r in resolve.run(open_ledger(root=project.root))])
    print("CLI check:", project.cl("check"))


# --- G. an uppercase sha pin ----------------------------------------------------------


def test_g_uppercase_pin(project):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts")
    up = _rev(project, "HEAD").upper()
    print("git rev-parse uppercase:", subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", "--verify", "--quiet", up],
        capture_output=True, text=True).returncode)
    build(project, ["experiment: docs/note-001.md @{pin}"], pin=up)
    print("UPPERCASE:", outcomes(project))
    print("RESOLVE:", [r.message for r in resolve.run(open_ledger(root=project.root))])


# --- H. duplicated heading -------------------------------------------------------------


def test_h_duplicate_heading(project):
    dup = NOTE + "\n## Observation\n\nA second run gave 0.05.\n"
    (project.root / "docs" / "note-001.md").write_text(dup, encoding="utf-8")
    build(project, ['lab: docs/note-001.md § "Observation" @{pin}'])
    (project.root / "docs" / "note-001.md").write_text(
        dup.replace("0.05", "0.50"), encoding="utf-8"
    )
    print("SECOND COPY EDITED:", outcomes(project))


# --- round 2 ---------------------------------------------------------------------------


def test_b3_staged_edit_reverted_worktree(project):
    build(project, ["experiment: docs/note-001.md @{pin}"])
    art = project.root / "docs" / "note-001.md"
    art.write_text(NOTE.replace("0.04", "0.09"), encoding="utf-8")
    project.git("add", "docs/note-001.md")
    art.write_text(NOTE, encoding="utf-8")  # the index has the drift, the tree does not
    print("STAGED DRIFT, CLEAN TREE:", outcomes(project))
    print("check --cached exit:", project.cl("check", "--cached"))
    print("git diff --cached:", subprocess.run(
        ["git", "-C", str(project.root), "diff", "--cached", "--name-only"],
        capture_output=True, text=True).stdout)


def test_a3_glob_decoy(project):
    (project.root / "docs" / "note[1].md").write_text(NOTE, encoding="utf-8")
    (project.root / "docs" / "note1.md").write_text(NOTE, encoding="utf-8")
    build(project, ["experiment: docs/note[1].md @{pin}"])
    (project.root / "docs" / "note1.md").write_text(NOTE.replace("0.04", "0.09"), "utf-8")
    print("DECOY EDITED:", outcomes(project))


def test_p_revert_after_discharge(project):
    path, _ = build(project, ["experiment: docs/note-001.md @{pin}"])
    art = project.root / "docs" / "note-001.md"
    art.write_text(NOTE.replace("0.04", "0.09"), encoding="utf-8")
    print("DRIFTED:", outcomes(project, write=True))
    project.git("add", "-A")
    project.git("commit", "-qm", "remeasure and discharge")
    print("AFTER DISCHARGE:", outcomes(project))
    art.write_text(NOTE, encoding="utf-8")  # the edit is undone
    print("AFTER REVERT:", outcomes(project))
    print("CLI check:", project.cl("check"))


def test_q_blob_pin(project):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts")
    blob = subprocess.run(
        ["git", "-C", str(project.root), "rev-parse", "HEAD:docs/note-001.md"],
        capture_output=True, text=True, check=True).stdout.strip()
    build(project, ["experiment: docs/note-001.md @{pin}"], pin=blob)
    print("BLOB PIN freshness:", outcomes(project))
    print("BLOB PIN resolve:", [(r.outcome, r.message) for r in
                                resolve.run(open_ledger(root=project.root))])


def test_r_pin_not_ancestor(project):
    """The pin is a descendant of HEAD: `pin..HEAD` counts nothing, but the drift is
    committed all the same."""
    build(project, ["experiment: docs/note-001.md @{pin}"])
    (project.root / "docs" / "note-001.md").write_text(NOTE.replace("0.04", "0.09"), "utf-8")
    project.git("add", "-A")
    project.git("commit", "-qm", "remeasure")
    later = _rev(project, "--short", "HEAD")
    path = next(project.entries.glob("A0001-*.md"))
    print("BEFORE:", outcomes(project))
    # Repin at the later commit and then move HEAD back before it.
    text = path.read_text(encoding="utf-8")
    old = text.split("@")[1].split("\n")[0].split("`")[0]
    print("later:", later, "old:", old)


def test_s_annotated_tag(project):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts")
    project.git("tag", "-a", "v1.0", "-m", "release")
    build(project, ["experiment: docs/note-001.md @v1.0"], pin="v1.0")
    (project.root / "docs" / "note-001.md").write_text(NOTE.replace("0.04", "0.09"), "utf-8")
    print("ANNOTATED TAG:", outcomes(project))


def test_t_nonexistent_named_pin(project):
    build(project, ["experiment: docs/note-001.md @v9.9"], pin="v9.9")
    print("MISSING NAMED PIN freshness:", outcomes(project))
    print("MISSING NAMED PIN resolve:", [(r.outcome, r.message) for r in
                                         resolve.run(open_ledger(root=project.root))])
    print("MISSING HEX PIN — repin to deadbeef")


def test_t2_nonexistent_hex_pin(project):
    build(project, ["experiment: docs/note-001.md @deadbeef"], pin="deadbeef")
    print("MISSING HEX PIN freshness:", outcomes(project))
    print("MISSING HEX PIN resolve:", [(r.outcome, r.message) for r in
                                       resolve.run(open_ledger(root=project.root))])


def test_u_cannot_remove_the_orphan_verdict(project):
    path, _ = build(project, ["experiment: docs/note-001.md @{pin}"])
    art = project.root / "docs" / "note-001.md"
    art.write_text(NOTE.replace("0.04", "0.09"), encoding="utf-8")
    outcomes(project, write=True)
    project.git("add", "-A")
    project.git("commit", "-qm", "remeasure and discharge")
    art.write_text(NOTE, encoding="utf-8")
    print("ORPHAN:", outcomes(project))
    # Try to clear it the only way there is: remove the verdict.
    text = path.read_text(encoding="utf-8")
    start = text.index("- 20")
    end = text.index("## References")
    path.write_text(text[:start] + text[end:], encoding="utf-8")
    print("AFTER REMOVING THE VERDICT, validate:",
          [(r.outcome, r.message) for r in validate.run(open_ledger(root=project.root))])
    print("CLI check:", project.cl("check"))
