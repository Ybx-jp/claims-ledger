"""QE6 — Part 2d: attack MEDIUM-34's fix. `ever_drifted()` asks only "did any commit
between the pin and HEAD touch the artifact's path at all" -- not whether the touch
happened BEFORE the verdict, and not whether it was substantive. If a pre-emptively
forged verdict can be laundered by a later no-op edit+revert (or a mode change, rename,
merge, etc.), the orphan rule's whole reason to exist is defeated."""

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


def append_forged_verdict(path, pointer_line, note="propagated from a moved ground"):
    text = path.read_text(encoding="utf-8")
    head, marker, tail = text.partition("\n## References")
    block = (
        "- 2026-01-01T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
        f"  evidence: {pointer_line}\n"
        f"  note: {note}\n"
    )
    path.write_text(head.rstrip("\n") + "\n\n" + block + marker + tail, encoding="utf-8")


def build_pinned_entry(project):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts")
    pin = _rev(project, "--short", "HEAD")
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
    return path, pin


def test_forge_then_launder_via_noop_edit_revert(project):
    art = project.root / "docs" / "note-001.md"
    path, pin = build_pinned_entry(project)

    # Step 1: pre-emptively forge a "contested" verdict WITHOUT ever having edited the
    # artifact -- exactly the attack the orphan rule exists to stop.
    append_forged_verdict(path, f"experiment: docs/note-001.md @{pin}")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "forge the discharge before anything moved")

    caught = outcomes(project)
    print("STEP 1 -- forged verdict, artifact never touched:", caught)
    assert caught and caught[0][0] == "fail" and "orphan" in caught[0][2]
    print("  -> correctly caught as an orphan (not yet laundered)")

    # Step 2: launder it. A commit that touches the artifact's path but leaves its bytes
    # identical to the pin -- append a trailing space, then remove it. Two commits, net
    # content change = none.
    original = art.read_text(encoding="utf-8")
    art.write_text(original + " ", encoding="utf-8")
    project.git("add", "-A")
    project.git("commit", "-qm", "trivial touch #1")
    art.write_text(original, encoding="utf-8")
    project.git("add", "-A")
    project.git("commit", "-qm", "trivial touch #2 -- reverts to byte-identical")

    after = outcomes(project)
    print("STEP 2 -- after a no-op touch+revert AFTER the forged verdict:", after)
    if after == []:
        print(
            "CONFIRMED FORGERY: the pre-emptively forged verdict is now silently accepted "
            "-- ever_drifted() only asks whether the path was EVER touched between the pin "
            "and HEAD, with no requirement that the touch happened before the verdict or "
            "that it changed anything. The orphan rule's stated purpose (stopping a "
            "verdict written before the ground moved) is defeated by any later no-op edit."
        )
    else:
        print("Not laundered -- still reported:", after)


def test_forge_then_launder_via_mode_change(project):
    art = project.root / "docs" / "note-001.md"
    path, pin = build_pinned_entry(project)
    append_forged_verdict(path, f"experiment: docs/note-001.md @{pin}")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "forge the discharge before anything moved")
    print("MODE-CHANGE before:", outcomes(project))

    art.chmod(0o755)
    project.git("add", "-A")
    project.git("commit", "-qm", "chmod +x, content unchanged")
    after = outcomes(project)
    print("MODE-CHANGE after chmod +x only:", after)


def test_forge_then_launder_via_rename_and_back(project):
    art = project.root / "docs" / "note-001.md"
    path, pin = build_pinned_entry(project)
    append_forged_verdict(path, f"experiment: docs/note-001.md @{pin}")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "forge the discharge before anything moved")
    print("RENAME before:", outcomes(project))

    moved = project.root / "docs" / "note-001-renamed.md"
    project.git("mv", "docs/note-001.md", "docs/note-001-renamed.md")
    project.git("commit", "-qm", "rename away")
    project.git("mv", "docs/note-001-renamed.md", "docs/note-001.md")
    project.git("commit", "-qm", "rename back")
    after = outcomes(project)
    print("RENAME after rename-away-and-back:", after)
