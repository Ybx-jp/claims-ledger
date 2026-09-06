"""Hypothesis 7: two writers racing on one file. Temp names are `.{name}.claims-ledger-
{pid}` -- different OS processes get different pids so no temp-name collision (and there
is no threading anywhere in the package -- grep confirms). Confirm: (a) no corruption
when two `sha --write` processes race on the same entry (bytes are always one writer's
complete output, never interleaved), and (b) whether a losing writer that reports success
lost the other's work silently (expected/inherent, not new -- the audit already reviewed
this class for propagate/freshness and called it self-announcing)."""
import sys, tempfile, subprocess, threading
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

tmp = Path(tempfile.mkdtemp())
p = make(tmp, git=False)
assert p.cl("new", "a-claim") == 0
a = p.entry("A0001-a-claim.md")
p.write_full_entry(a)

# Prepare two DIFFERENT full-file variants (both currently valid re-writes) to run
# `sha --write` against concurrently by editing the file differently just before each
# subprocess starts, then racing them.
base = a.read_text(encoding="utf-8")

variant1 = base.replace("cohort: the synthetic graph of these tests", "cohort: variant one")
variant2 = base.replace("cohort: the synthetic graph of these tests", "cohort: variant two")

CODE = (
    "import sys, time\n"
    "sys.path.insert(0, {tests!r})\n"
    "text = open(sys.argv[2]).read()\n"
    "open(sys.argv[1], 'w').write(text)\n"
    "from claims_ledger import cli\n"
    "sys.exit(cli.main(['--root', sys.argv[3], 'sha', '--write', sys.argv[1]]))\n"
).format(tests=str(Path(__file__).resolve().parents[2] / "tests"))

v1f = tmp / "v1.md"; v1f.write_text(variant1, encoding="utf-8")
v2f = tmp / "v2.md"; v2f.write_text(variant2, encoding="utf-8")

results = {}
def run(tag, vfile):
    r = subprocess.run([sys.executable, "-c", CODE, str(a), str(vfile), str(p.root)],
                        capture_output=True, text=True)
    results[tag] = r

t1 = threading.Thread(target=run, args=("one", v1f))
t2 = threading.Thread(target=run, args=("two", v2f))
t1.start(); t2.start(); t1.join(); t2.join()

for tag in ("one", "two"):
    r = results[tag]
    print(f"writer {tag}: rc={r.returncode} stdout={r.stdout.strip()!r} stderr={r.stderr.strip()!r}")

final = a.read_text(encoding="utf-8")
is_v1 = "cohort: variant one" in final
is_v2 = "cohort: variant two" in final
is_corrupt = not (is_v1 or is_v2) or (is_v1 and is_v2)
print("final file is exactly variant one:", is_v1, " variant two:", is_v2)
print("file corrupted / interleaved:", is_corrupt)
print("check rc on final state:", p.cl("check"))
both_reported_success = all(results[t].returncode == 0 for t in ("one", "two"))
print("both writers reported rc=0:", both_reported_success,
      "(last-writer-wins is expected; corruption would not be)")
