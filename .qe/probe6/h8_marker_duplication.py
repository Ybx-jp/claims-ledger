"""Hypothesis 8: attack append_verdict's new marker discipline (and the immutability
checker it shares its boundary logic with). Both `propagate.append_verdict` and
`validate._frozen_region`/`_frozen_bytes` locate the "frozen region" the same way:
`text.partition(APPEND)` -- the FIRST literal occurrence of the marker string. If the
committed entry happens to quote the marker string once, early, inside its own Backing
section (plausible: a citation/backing quote *about* the claims-ledger format itself, or
any source excerpt that happens to contain that literal line), everything from that fake
occurrence onward -- including the real marker, the real Verdicts/References sections,
and any legitimate frozen content in between the fake occurrence and the real marker --
is no longer inside what either function calls `head`.

Case A: does `check` (validate.check_history, HIGH-39's own fix) still catch a hand-edit
made to committed content that sits between the fake early marker and the real one?
Case B: two real markers is fine (established already by partition on FIRST occurrence
consistently) -- included for completeness.
"""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

APPEND = "<!-- APPEND BELOW THIS LINE ONLY -->"


def case_a():
    print("=== Case A: a fake marker quoted early in Backing, then a hand-edit between it and the real marker ===")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    assert p.cl("new", "a-claim") == 0
    a = p.entry("A0001-a-claim.md")
    p.write_full_entry(a)
    text = a.read_text(encoding="utf-8")
    # Insert a Backing bullet that quotes the marker text verbatim, as a source excerpt
    # would if the source itself documents this ledger's own file format. This sits
    # ABOVE the real APPEND marker, inside the frozen Backing section.
    fake_quote = (
        '- source: fx-source · whole text\n'
        '  speaker: Okafor\n'
        f'  quote: "the template ends its frozen region with {APPEND}"\n'
    )
    text = text.replace("## Backing\n\n", "## Backing\n\n" + fake_quote)
    a.write_text(text, encoding="utf-8")
    assert p.cl("sha", "--write", str(a)) == 0
    p.git("init", "-q"); p.git("add", "-A"); p.git("commit", "-qm", "sealed, with a quoted marker in Backing")
    print("check right after commit (want 0):", p.cl("check"))

    raw = a.read_bytes()
    fake_pos = raw.find(APPEND.encode())
    real_pos = raw.rfind(APPEND.encode())
    print("fake marker byte offset:", fake_pos, " real marker byte offset:", real_pos,
          " (two distinct occurrences:", fake_pos != real_pos, ")")

    # Hand-edit the Assertion (well above the real marker but AFTER the fake marker's
    # end) -- a byte that check's docstring says is immutable once committed.
    tail_after_fake = raw[fake_pos + len(APPEND):]
    head_incl_fake = raw[: fake_pos + len(APPEND)]
    # "Okafor" is the speaker on the REAL Backing bullet, which sits after the fake
    # quoted marker and before the real marker -- legitimately frozen, committed content.
    assert b"Okafor" in tail_after_fake, "sanity: the real Backing bullet sits after the fake marker"
    assert real_pos > fake_pos + len(APPEND), "sanity: the real marker is further still"
    mutated_tail = tail_after_fake.replace(b"Okafor", b"NOT-OKAFOR-TAMPERED", 1)
    assert mutated_tail != tail_after_fake
    mutated = head_incl_fake + mutated_tail
    assert mutated != raw
    a.write_bytes(mutated)

    rc = p.cl("check")
    print("check AFTER hand-editing the (real, committed, above-the-true-marker) Assertion text:", rc)
    if rc == 0:
        print("!!! check_history did not catch a tamper to content between the fake marker")
        print("!!! and the real one -- the immutable region shrank to the bytes before the")
        print("!!! FIRST literal occurrence of the marker string, not the real boundary")
    else:
        print("check_history caught it")


def case_b_two_real_markers():
    print("\n=== Case B: sanity -- two REAL markers (second one typed by hand after the first) ===")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    assert p.cl("new", "a-claim") == 0
    a = p.entry("A0001-a-claim.md")
    p.write_full_entry(a)
    text = a.read_text(encoding="utf-8")
    text = text.replace(APPEND, APPEND + "\n" + APPEND, 1)
    a.write_text(text, encoding="utf-8")
    print("validate on an entry with the marker duplicated verbatim:", p.cl("check"))


if __name__ == "__main__":
    case_a()
    case_b_two_real_markers()
