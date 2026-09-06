import sys, tempfile, shutil, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make
def sec(t): print("\n=== " + t + " ===")

def two_entry(tmp, commit=True):
    p = make(tmp, git=False)
    assert p.cl("new","a-claim") == 0
    a = p.entry("A0001-a-claim.md"); p.write_full_entry(a)
    assert p.cl("new","b-claim") == 0
    b = p.entry("A0002-b-claim.md")
    t = b.read_text(encoding="utf-8")
    t = t.replace("TODO: the claim, in this project's words. No quotation marks.","The first claim is unsupported.")
    t = t.replace("metric: TODO","metric: m").replace("cohort: TODO","cohort: c").replace("condition: TODO","condition: d")
    t = t.replace("- TODO: one typed pointer per line",'- lab: docs/note-001.md § "Observation" @working\n- entry: A0001-a-claim · challenges')
    t = t.replace("TODO: the rule by which the grounds support the assertion.","Because the grounds were withdrawn.")
    b.write_text(t, encoding="utf-8"); assert p.cl("sha","--write",str(b)) == 0
    if commit:
        p.git("init","-q"); p.git("add","-A"); p.git("commit","-qm","sealed")
    return p, a, b

sec("A propagate --write twice (idempotency)")
p,a,b = two_entry(Path(tempfile.mkdtemp()))
p.cl("propagate","--write"); n1 = a.read_text(encoding="utf-8").count("· contested ·")
p.cl("propagate","--write"); n2 = a.read_text(encoding="utf-8").count("· contested ·")
print("verdicts after 1st, 2nd:", n1, n2)

sec("B duplicate id via a second file with the same id prefix")
p,a,b = two_entry(Path(tempfile.mkdtemp()), commit=False)
shutil.copyfile(a, p.entries/"A0001-clash.md")
print("check rc:", p.cl("check"))

sec("C entries/ symlink aliasing one file: two 'entries', one inode")
p,a,b = two_entry(Path(tempfile.mkdtemp()), commit=False)
(p.entries/"A0003-alias.md").symlink_to(a.name)
before = a.read_text(encoding="utf-8").count("· contested ·")
rc = p.cl("propagate","--write")
print("rc", rc, "verdicts in A0001 before/after:", before, a.read_text(encoding="utf-8").count("· contested ·"))
print("check rc:", p.cl("check"))

sec("D source add over a cache file with wrong bytes -> downstream")
tmp = Path(tempfile.mkdtemp()); p = make(tmp, git=False)
s2 = tmp/"s2.txt"; s2.write_text("The real bytes.\n", encoding="utf-8")
dig = hashlib.sha256(s2.read_bytes()).hexdigest()
(p.root/"ledger"/"cache"/dig).write_text("TRUNCATED", encoding="utf-8")
print("source add rc:", p.cl("source","add",str(s2),"--id","fx-2","--type","paper","--citation","C","--authors","A"))
print("stored bytes:", (p.root/"ledger"/"cache"/dig).read_text())
