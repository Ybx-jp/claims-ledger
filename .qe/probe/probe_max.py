"""How much can be hidden in the region no section owns?"""

PAYLOAD = """
# Assertion

Degree, not the stale fraction, governs the aggregation error. The section below is
superseded and is kept only for the record; do not cite it.

> Reviewer's note: the grounds were withdrawn on 2026-09-06.
"""


def test_maximal_preamble_payload(project, capsys):
    p = project
    assert p.cl("new", "a-claim") == 0
    path = p.write_full_entry(p.entry("A0001-a-claim.md"))
    p.git("init", "-q")
    p.git("add", "-A")
    p.git("commit", "-qm", "sealed")
    assert p.cl("check") == 0
    sealed = path.read_bytes()

    head, rest = path.read_text(encoding="utf-8").split("\n## Assertion", 1)
    path.write_text(head + PAYLOAD + "\n## Assertion" + rest, encoding="utf-8")

    capsys.readouterr()
    rc = p.cl("check")
    out = capsys.readouterr()
    print("=== check after tampering a committed entry ===")
    print("exit", rc)
    print(out.out.strip() or "(no stdout)")
    print(out.err.strip() or "(no stderr)")
    print("=== bytes changed:", len(path.read_bytes()) - len(sealed))
    print("=== what a reader now sees ===")
    print(path.read_text(encoding="utf-8")[:700])
    assert 0, "probe"
