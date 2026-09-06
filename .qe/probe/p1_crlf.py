import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

tmp = Path(tempfile.mkdtemp())
p = make(tmp, git=False)
assert p.cl("new", "a-claim") == 0
path = p.entry("A0001-a-claim.md")
p.write_full_entry(path)
# make it CRLF on disk
raw = path.read_bytes()
path.write_bytes(raw.replace(b"\n", b"\r\n"))
p.git("init", "-q"); p.git("add", "-A"); p.git("commit", "-qm", "committed with CRLF")
print("check on CRLF committed:", p.cl("check"))
before = path.read_bytes()
print("CRLF count before:", before.count(b"\r\n"))

# now provoke propagate --write: need a fallen ground. Simpler: run sha --write after editing Scope? that's refused (committed).
# Instead: freshness/propagate. Try a second entry that challenges the first.
assert p.cl("new", "b-claim") == 0
b = p.entry("A0002-b-claim.md")
from conftest import ASSERTION
text = b.read_text(encoding="utf-8")
text = text.replace("TODO: the claim, in this project's words. No quotation marks.", "The first claim is not supported.")
text = text.replace("metric: TODO", "metric: m").replace("cohort: TODO", "cohort: c").replace("condition: TODO", "condition: d")
text = text.replace("- TODO: one typed pointer per line", "- lab: docs/note-001.md § \"Observation\" @working\n- entry: A0001-a-claim · challenges")
text = text.replace("TODO: the rule by which the grounds support the assertion.", "Because the grounds were withdrawn.")
b.write_text(text, encoding="utf-8")
assert p.cl("sha", "--write", str(b)) == 0
rc = p.cl("propagate", "--write")
print("propagate --write rc:", rc)
after = path.read_bytes()
print("CRLF count after:", after.count(b"\r\n"), "LF-only lines:", after.count(b"\n") - after.count(b"\r\n"))
print("check after propagate --write:", p.cl("check"))
print("---- git diff stat ----")
import subprocess
print(subprocess.run(["git","-C",str(p.root),"diff","--stat"],capture_output=True,text=True).stdout)
