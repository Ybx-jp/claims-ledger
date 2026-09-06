"""Probe: does a git that cannot answer `rev-list` suppress the orphan report —
the forged-discharge check — without saying so?"""

import os
import subprocess

from claims_ledger import freshness
from claims_ledger.schema import open_ledger

from test_freshness import *  # noqa: F401,F403  (brings the `pinned` fixture in)


FORGERY = (
    "- 2026-11-20T09:00:00-08:00 · contested · grade: measured · author: propagation\n"
    '  evidence: lab: docs/note-001.md § "Observation" @{pin}\n'
    "  note: propagated from a moved ground\n"
)


def shim_git(tmp_path, failing_arg):
    d = tmp_path / "bin"
    d.mkdir(exist_ok=True)
    real = subprocess.run(["which", "git"], capture_output=True, text=True).stdout.strip()
    (d / "git").write_text(
        "#!/bin/sh\n"
        f'for a in "$@"; do [ "$a" = "{failing_arg}" ] && exit 128; done\n'
        f'exec {real} "$@"\n'
    )
    (d / "git").chmod(0o755)
    return d


def test_probe_orphan_normally(pinned):
    pinned.append(FORGERY.format(pin=pinned.pin))
    got = pinned.outcomes()
    print("\nNORMAL:", got)
    assert [o for o, _, _ in got] == ["fail"], got


def test_probe_orphan_when_rev_list_cannot_answer(pinned, tmp_path):
    pinned.append(FORGERY.format(pin=pinned.pin))
    d = shim_git(tmp_path, "rev-list")
    old = os.environ["PATH"]
    os.environ["PATH"] = f"{d}:{old}"
    try:
        reports = freshness.run(open_ledger(root=pinned.root))
        got = [(r.outcome, r.part, r.message) for r in reports]
    finally:
        os.environ["PATH"] = old
    print("\nREV-LIST BROKEN:", got)
    assert [o for o, _, _ in got] == ["fail"], got
