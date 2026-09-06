"""Hypothesis 3: SIGKILL mid-write leaves a `.{name}.claims-ledger-{pid}` temp file
beside the target. Does anything COLLECT it (entry discovery, `documents` globs, the
freshness artifact scan, `corpus`)? A stray file a checker reads is a false failure; one
it silently skips may be a false pass."""
import sys, tempfile, os, signal, subprocess, time, glob as globmod
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

CHILD = r"""
import sys, os, time
from claims_ledger import cli
sys.path.insert(0, {tests!r})
# Monkeypatch os.fsync to pause right after the temp file is opened and partially
# written, so the parent has a window to SIGKILL us mid-write, leaving the temp file
# behind and the rename never having happened.
import claims_ledger.schema as schema
_orig_fsync = os.fsync
def slow_fsync(fd):
    sys.stderr.write("about to fsync\n"); sys.stderr.flush()
    time.sleep(5)
    return _orig_fsync(fd)
os.fsync = slow_fsync
sys.exit(cli.main(["--root", sys.argv[1], "sha", "--write", sys.argv[2]]))
"""

tmp = Path(tempfile.mkdtemp())
p = make(tmp, git=False)
assert p.cl("new", "a-claim") == 0
a = p.entry("A0001-a-claim.md")
p.write_full_entry(a)
t = a.read_text(encoding="utf-8")
t = t.replace("cohort: the synthetic graph of these tests", "cohort: edited")
a.write_text(t, encoding="utf-8")
before = a.read_bytes()

script = CHILD.format(tests=str(Path(__file__).resolve().parents[2] / "tests"))
proc = subprocess.Popen([sys.executable, "-c", script, str(p.root), str(a)],
                         stderr=subprocess.PIPE, text=True)
# wait until it signals it's about to fsync (i.e., temp file written, not yet renamed)
line = proc.stderr.readline()
print("child said:", line.strip())
time.sleep(0.3)
proc.kill()  # SIGKILL
proc.wait()
print("child killed, returncode:", proc.returncode)

after = a.read_bytes()
print("target file unchanged:", before == after)
leftovers = [f.name for f in a.parent.iterdir() if "claims-ledger-" in f.name]
print("leftover temp file(s):", leftovers)

if leftovers:
    stray = a.parent / leftovers[0]
    print("stray file size:", stray.stat().st_size, "starts with dot:", stray.name.startswith("."))

    # Does entry discovery pick it up?
    rc = p.cl("check")
    print("\ncheck rc with stray temp file present:", rc)
    rc2 = p.cl("status")
    print("status rc with stray temp file present:", rc2)

    # Does the `documents` glob (default "*.md", "docs/*.md") pick it up if we rename
    # the stray to also live at the project root ending in .md-lookalike? Test as-is first.
    import glob as g
    root_docs = g.glob(str(p.root / "*.md")) + g.glob(str(p.root / "docs" / "*.md"))
    print("documents glob at project root/docs matches stray:", any(leftovers[0] in x for x in root_docs))

    # Does list_entry_files (entries/ scan) pick it up?
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
    from claims_ledger.schema import list_entry_files
    listed = [str(x) for x in list_entry_files(p.entries)]
    print("list_entry_files sees the stray:", any(leftovers[0] in x for x in listed))

    stray.unlink()
    print("\n(cleaned up stray file for hygiene)")
else:
    print("no leftover temp file observed with this timing; widen the sleep window")
