import sys, tempfile, os, hashlib, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

def sec(t): print("\n=== " + t + " ===")

# --- A: cache file already present with wrong bytes -> source add exits 0 over bytes it did not write
sec("A cache prefilled with wrong bytes")
tmp = Path(tempfile.mkdtemp()); p = make(tmp, git=False)
s2 = tmp/"s2.txt"; s2.write_text("The real bytes of the second source.\n", encoding="utf-8")
dig = hashlib.sha256(s2.read_bytes()).hexdigest()
(p.root/"ledger"/"cache"/dig).write_text("TRUNCATED", encoding="utf-8")
rc = p.cl("source","add",str(s2),"--id","fx-2","--type","paper","--citation","C","--authors","A")
print("rc:", rc, "cache content:", (p.root/"ledger"/"cache"/dig).read_text())

# --- B: two `new` runs racing for the same id (sequential simulation of the race)
sec("B two `new` in parallel")
tmp = Path(tempfile.mkdtemp()); p = make(tmp, git=False)
assert p.cl("new","one") == 0
procs = [subprocess.Popen([sys.executable,"-c",
    f"from claims_ledger import cli; raise SystemExit(cli.main(['--root',{str(p.root)!r},'new',{slug!r}]))"],
    capture_output := None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for slug in ("two","three")]
for pr in procs: pr.wait()
print(sorted(x.name for x in p.entries.iterdir()))
print("check rc:", p.cl("check"))

# --- C: entry path is a directory
sec("C entry replaced by a directory")
tmp = Path(tempfile.mkdtemp()); p = make(tmp, git=False)
(p.entries/"A0001-x.md").mkdir()
print("new rc:", p.cl("new","x"))

# --- D: read-only entries dir, `new`
sec("D read-only entries dir")
tmp = Path(tempfile.mkdtemp()); p = make(tmp, git=False)
os.chmod(p.entries, 0o555)
print("new rc:", p.cl("new","y"))
os.chmod(p.entries, 0o755)

# --- E: init twice (idempotency), and init --force over a populated ledger
sec("E init twice")
tmp = Path(tempfile.mkdtemp()); p = make(tmp, git=False)
before = sorted((str(x.relative_to(p.root)), x.stat().st_size) for x in p.root.rglob("*") if x.is_file())
print("init again rc:", p.cl("init"))
print("init --force rc:", p.cl("init","--force"))
after = sorted((str(x.relative_to(p.root)), x.stat().st_size) for x in p.root.rglob("*") if x.is_file())
print("same tree:", before == after)

# --- F: hook install when .git/hooks is a file
sec("F hook install, hooks is a file")
tmp = Path(tempfile.mkdtemp()); p = make(tmp, git=False); p.git("init","-q")
hooks = p.root/".git"/"hooks"
import shutil as sh
sh.rmtree(hooks); hooks.write_text("not a dir", encoding="utf-8")
print("hook --install rc:", p.cl("hook","--install"))
