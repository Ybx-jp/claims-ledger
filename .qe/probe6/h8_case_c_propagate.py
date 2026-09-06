"""Hypothesis 8, case C: does propagate --write actually complete correctly (insert
below the REAL marker, not the fake earlier one; not falsely self-refuse) when the
committed entry's Backing legitimately quotes the marker string once, early?"""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

APPEND = "<!-- APPEND BELOW THIS LINE ONLY -->"

tmp = Path(tempfile.mkdtemp())
p = make(tmp, git=False)
assert p.cl("new", "a-claim") == 0
a = p.entry("A0001-a-claim.md")
p.write_full_entry(a)
text = a.read_text(encoding="utf-8")
fake_note = f"note-about-format: {APPEND}\n"
# Put the fake marker literal as an unstructured line -- validate will flag Backing's
# shape (out of scope here), but the point is purely whether the marker-boundary logic
# in append_verdict behaves. Placed at the very start of Backing.
text = text.replace("## Backing\n\n", "## Backing\n\n" + fake_note)
a.write_text(text, encoding="utf-8")
p.cl("sha", "--write", str(a))
p.git("init", "-q"); p.git("add", "-A"); p.git("commit", "-qm", "sealed, fake marker text in Backing")

assert p.cl("new", "b-claim") == 0
b = p.entry("A0002-b-claim.md")
t = b.read_text(encoding="utf-8")
t = t.replace("TODO: the claim, in this project's words. No quotation marks.", "The first claim is unsupported.")
t = t.replace("metric: TODO", "metric: m").replace("cohort: TODO", "cohort: c").replace("condition: TODO", "condition: d")
t = t.replace("- TODO: one typed pointer per line", '- lab: docs/note-001.md § "Observation" @working\n- entry: A0001-a-claim · challenges')
t = t.replace("TODO: the rule by which the grounds support the assertion.", "Because the grounds were withdrawn.")
b.write_text(t, encoding="utf-8")
p.cl("sha", "--write", str(b))

before = a.read_bytes()
rc = p.cl("propagate", "--write")
after = a.read_bytes()
print("propagate --write rc:", rc)
print("bytes were appended:", len(after) > len(before))
print("verdict landed after the REAL (last) marker occurrence:")
real_marker_end = after.rfind(APPEND.encode()) + len(APPEND.encode())
verdict_pos = after.find(b"contested")
print("  real marker ends at byte", real_marker_end, " verdict block starts at byte", verdict_pos,
      " (verdict after real marker:", verdict_pos > real_marker_end, ")")
print("frozen content up to and including the REAL marker unchanged:",
      before[: after.rfind(APPEND.encode()) + len(APPEND.encode())]
      == after[: after.rfind(APPEND.encode()) + len(APPEND.encode())])
