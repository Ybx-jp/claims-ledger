import sys, tempfile, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make
def sec(t): print("\n=== " + t + " ===")

sec("A entry symlinked outside the root: sha --write and propagate --write")
tmp = Path(tempfile.mkdtemp()); p = make(tmp, git=False)
assert p.cl("new","a-claim") == 0
a = p.entry("A0001-a-claim.md"); p.write_full_entry(a)
outside = tmp/"outside.md"
outside.write_text(a.read_text(encoding="utf-8").replace("metric: mean","metric: changed"), encoding="utf-8")
a.unlink(); a.symlink_to(outside)
snap = outside.read_bytes()
print("sha --write rc:", p.cl("sha","--write",str(a)))
print("outside unchanged:", outside.read_bytes() == snap)

sec("B init into a read-only project root")
tmp = Path(tempfile.mkdtemp()); root = tmp/"ro"; root.mkdir(); os.chmod(root, 0o555)
from conftest import Project
print("init rc:", Project(root).cl("init"))
os.chmod(root, 0o755)

sec("C non-ASCII / bytes round trip through sha --write")
tmp = Path(tempfile.mkdtemp()); p = make(tmp, git=False)
assert p.cl("new","u-claim") == 0
u = p.entry("A0001-u-claim.md")
t = u.read_text(encoding="utf-8")
t = t.replace("TODO: the claim, in this project's words. No quotation marks.","Naïve — éàü 中文 \U0001f600 holds.")
t = t.replace("metric: TODO","metric: μ‑error").replace("cohort: TODO","cohort: c").replace("condition: TODO","condition: d")
t = t.replace("- TODO: one typed pointer per line",'- lab: docs/note-001.md § "Observation" @working')
t = t.replace("TODO: the rule by which the grounds support the assertion.","Because.")
u.write_text(t, encoding="utf-8")
before = u.read_bytes()
p.cl("sha","--write",str(u))
after = u.read_bytes()
import re
b2 = re.sub(rb"verbatim_sha: [0-9a-f]+", b"X", before); a2 = re.sub(rb"verbatim_sha: [0-9a-f]+", b"X", after)
print("bytes outside the sha line preserved:", b2 == a2)

sec("D entry with no trailing newline through propagate --write")
