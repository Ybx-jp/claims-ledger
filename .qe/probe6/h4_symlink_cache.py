"""Hypothesis 4: write_bytes_atomically resolves os.path.realpath(path) and writes to the
RESOLVED target. Every caller in authoring.restamp / propagate.append_verdict asks
leaves_root BEFORE the write -- but register_source's cache write
(`write_bytes_atomically(stored, data)` in authoring.py) has NO leaves_root check at all.
The cache filename is content-addressed (sha256 hex), so an attacker who can plant a
dangling symlink at `cache/<digest>` pointing outside the project (e.g. via a malicious
git clone shipping that symlink) gets an out-of-root write the moment someone runs
`source add` with matching bytes."""
import sys, tempfile, hashlib, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

tmp = Path(tempfile.mkdtemp())
p = make(tmp, git=False)

outside_dir = tmp / "outside"
outside_dir.mkdir()
target_outside = outside_dir / "pwned.txt"
assert not target_outside.exists()

content = b"content whose sha256 will name the cache entry\n"
digest = hashlib.sha256(content).hexdigest()
cache = p.root / "ledger" / "cache"
cache.mkdir(parents=True, exist_ok=True)
symlink_path = cache / digest
os.symlink(target_outside, symlink_path)  # dangling symlink, cache/<digest> -> outside/pwned.txt
print("planted dangling symlink:", symlink_path, "->", os.readlink(symlink_path))
print("symlink_path.exists() (follows symlink):", symlink_path.exists())

src_file = tmp / "source.txt"
src_file.write_bytes(content)

rc = p.cl("source", "add", str(src_file), "--id", "fx-evil", "--type", "paper",
          "--citation", "C", "--authors", "A")
print("source add rc:", rc)
print("outside file now exists:", target_outside.exists())
if target_outside.exists():
    print("outside file content matches source bytes:", target_outside.read_bytes() == content)
    print("!!! source add wrote OUTSIDE the project root through a symlinked cache slot")
print("cache/<digest> is still a symlink (not replaced with a regular file in-tree):",
      symlink_path.is_symlink())
print("check rc:", p.cl("check"))
