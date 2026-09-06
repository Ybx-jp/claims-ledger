import sys, tempfile, os, resource, signal, subprocess, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

if len(sys.argv) > 1 and sys.argv[1] == "child":
    root, src = sys.argv[2], sys.argv[3]
    signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
    lim = int(os.environ["PROBE_LIMIT"]); resource.setrlimit(resource.RLIMIT_FSIZE, (lim, lim))
    from claims_ledger import cli
    sys.exit(cli.main(["--root", root, "source", "add", src, "--id", "fx-2",
                       "--type", "paper", "--citation", "C", "--authors", "A"]))

tmp = Path(tempfile.mkdtemp()); p = make(tmp, git=False)
big = tmp/"big.txt"; big.write_text("The bytes of the second source.\n"*80, encoding="utf-8")
dig = hashlib.sha256(big.read_bytes()).hexdigest()
env = dict(os.environ, PROBE_LIMIT="500")
r = subprocess.run([sys.executable, __file__, "child", str(p.root), str(big)], env=env, capture_output=True, text=True)
print("interrupted attempt rc:", r.returncode); print("stderr:", r.stderr.strip())
cache = p.root/"ledger"/"cache"/dig
print("cache file exists:", cache.exists(), "size:", cache.stat().st_size if cache.exists() else None, "wanted:", big.stat().st_size)
print("registry rows:", p.root.joinpath("ledger/sources.jsonl").read_text().count("\n"))
print("--- retry, no limit ---")
rc = p.cl("source","add",str(big),"--id","fx-2","--type","paper","--citation","C","--authors","A")
print("retry rc:", rc, "cache size now:", cache.stat().st_size)
# downstream: an entry quoting it
assert p.cl("new","q-claim") == 0
e = p.entry("A0001-q-claim.md"); t = e.read_text(encoding="utf-8")
t = t.replace("TODO: the claim, in this project's words. No quotation marks.","The bytes of the second source are what they are.")
t = t.replace("metric: TODO","metric: m").replace("cohort: TODO","cohort: c").replace("condition: TODO","condition: d")
t = t.replace("- TODO: one typed pointer per line","- source: fx-2 · whole text")
t = t.replace("TODO: the rule by which the grounds support the assertion.","Because the source says so.")
t = t.replace("## Backing\n\nnone", '## Backing\n\n- source: fx-2 · whole text\n  speaker: A\n  quote: "The bytes of the second source."')
e.write_text(t, encoding="utf-8"); p.cl("sha","--write",str(e))
print("check rc:", p.cl("check"))
