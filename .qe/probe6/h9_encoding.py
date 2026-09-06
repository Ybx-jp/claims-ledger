"""Hypothesis 9: read_text_exact(newline="") round-trips exotic line endings and BOM
byte-exact through sha --write and propagate --write. Cases: lone-CR (old Mac), mixed
CRLF/LF, a UTF-8 BOM, and no final newline."""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

APPEND = "<!-- APPEND BELOW THIS LINE ONLY -->"


def sha_write_case(label, transform):
    print(f"\n--- sha --write round-trip: {label} ---")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    assert p.cl("new", "a-claim") == 0
    a = p.entry("A0001-a-claim.md")
    p.write_full_entry(a)
    # write_full_entry already ran sha --write once (LF). Now transform the bytes,
    # re-stamp a *different* stale sha by touching Scope so `sha --write` has real work
    # to do, then transform, then run sha --write again and check every byte but the
    # verbatim_sha line round-trips.
    raw = a.read_bytes()
    mutated = transform(raw)
    a.write_bytes(mutated)
    before = a.read_bytes()
    rc = p.cl("sha", "--write", str(a))
    after = a.read_bytes()
    print("sha --write rc:", rc)
    # compare byte-for-byte except the verbatim_sha value itself (unchanged here, since
    # we did not edit Scope/Backing -- sha --write should be a no-op: declared==computed)
    print("file unchanged (declared already matched computed):", before == after)
    print("line-ending byte pattern preserved:", _fingerprint(before) == _fingerprint(after))


def _fingerprint(raw):
    return (raw.count(b"\r\n"), raw.count(b"\n") - raw.count(b"\r\n"), raw.count(b"\r") - raw.count(b"\r\n"))


def propagate_write_case(label, transform):
    print(f"\n--- propagate --write round-trip: {label} ---")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    assert p.cl("new", "a-claim") == 0
    a = p.entry("A0001-a-claim.md")
    p.write_full_entry(a)
    raw = a.read_bytes()
    mutated = transform(raw)
    a.write_bytes(mutated)
    p.git("init", "-q"); p.git("add", "-A"); p.git("commit", "-qm", "committed, transformed")
    before_frozen = a.read_bytes().split(APPEND.encode(), 1)[0] if APPEND.encode() in a.read_bytes() else None
    if before_frozen is None:
        print("SKIP: transform destroyed the APPEND marker itself, not a fair round-trip test")
        return

    assert p.cl("new", "b-claim") == 0
    b = p.entry("A0002-b-claim.md")
    with open(b, encoding="utf-8", newline="") as fh:
        t = fh.read()
    t = t.replace("TODO: the claim, in this project's words. No quotation marks.", "The first claim is unsupported.")
    t = t.replace("metric: TODO", "metric: m").replace("cohort: TODO", "cohort: c").replace("condition: TODO", "condition: d")
    t = t.replace("- TODO: one typed pointer per line", '- lab: docs/note-001.md § "Observation" @working\n- entry: A0001-a-claim · challenges')
    t = t.replace("TODO: the rule by which the grounds support the assertion.", "Because the grounds were withdrawn.")
    with open(b, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)
    p.cl("sha", "--write", str(b))

    rc = p.cl("propagate", "--write")
    after_frozen = a.read_bytes().split(APPEND.encode(), 1)[0]
    print("propagate --write rc:", rc)
    print("frozen region byte-identical across the write:", before_frozen == after_frozen)
    print("check rc:", p.cl("check"))


def to_lone_cr(raw):
    return raw.replace(b"\n", b"\r")


def to_mixed(raw):
    lines = raw.split(b"\n")
    out = []
    for i, ln in enumerate(lines[:-1]):
        out.append(ln + (b"\r\n" if i % 2 == 0 else b"\n"))
    out.append(lines[-1])
    return b"".join(out)


def to_bom(raw):
    return b"\xef\xbb\xbf" + raw


def to_no_final_newline(raw):
    return raw.rstrip(b"\n")


if __name__ == "__main__":
    sha_write_case("lone-CR (old Mac)", to_lone_cr)
    sha_write_case("mixed CRLF/LF", to_mixed)
    sha_write_case("UTF-8 BOM prefix", to_bom)
    sha_write_case("no final newline", to_no_final_newline)

    propagate_write_case("lone-CR (old Mac)", to_lone_cr)
    propagate_write_case("mixed CRLF/LF", to_mixed)
    propagate_write_case("UTF-8 BOM prefix", to_bom)
    propagate_write_case("no final newline", to_no_final_newline)
