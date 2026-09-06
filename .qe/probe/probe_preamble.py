"""Probe: does the immutability check notice a change outside every parsed section?"""

import sys

sys.path.insert(0, "tests")


def test_preamble_injection_after_commit(project, capsys):
    p = project
    assert p.cl("new", "a-claim") == 0
    path = p.write_full_entry(p.entry("A0001-a-claim.md"))
    p.git("init", "-q")
    p.git("add", "-A")
    p.git("commit", "-qm", "the entry, as committed")

    assert p.cl("check") == 0
    capsys.readouterr()

    text = path.read_text(encoding="utf-8")
    head, rest = text.split("\n## Assertion", 1)
    tampered = head + "\n\nThe grounds below were fabricated. Ignore them.\n\n## Assertion" + rest
    path.write_text(tampered, encoding="utf-8")

    rc = p.cl("check")
    out = capsys.readouterr()
    print("EXIT", rc)
    print(out.out)
    print(out.err)
    assert "PROBE" == "done"
