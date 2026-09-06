"""Probe: can a pre-emptive (forged) discharge be laundered by a no-op commit?"""
from claims_ledger import freshness
from claims_ledger.schema import open_ledger
from test_freshness import *  # noqa: F401,F403
import subprocess
def gitc(p, *a):
    subprocess.run(["git", "-C", str(p.root), *a], check=True, capture_output=True)

FORGERY = (
    "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
    '  evidence: lab: docs/note-001.md § "Observation" @{pin}\n'
    "  note: propagated from a moved ground\n"
)


def outs(root):
    return [(r.outcome, r.part, r.message) for r in freshness.run(open_ledger(root=root))]


def test_forgery_then_a_noop_edit_and_revert(pinned):
    """The artifact is never actually different from the pin. One commit touches it and
    one commit puts it back. Nothing about the ground has changed."""
    pinned.append(FORGERY.format(pin=pinned.pin))
    print("\n1. forged, artifact untouched:", outs(pinned.root))

    note = pinned.root / "docs" / "note-001.md"
    original = note.read_bytes()
    note.write_bytes(original.replace(b"0.04", b"0.99"))
    gitc(pinned, "add", "-A"); gitc(pinned, "commit", "-qm", "a touch")
    note.write_bytes(original)
    gitc(pinned, "add", "-A"); gitc(pinned, "commit", "-qm", "and back again")

    after = outs(pinned.root)
    print("2. after touch-and-revert (artifact byte-identical to the pin):", after)
    assert [o for o, _, _ in after] == ["fail"], (
        "the forged discharge is no longer reported: %r" % (after,)
    )
