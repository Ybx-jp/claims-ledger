"""Hypothesis 4, continued: does `claims-ledger new` (authoring.create_entry) check
leaves_root before writing? create_entry never calls refuse_to_write_outside_the_root.
Test: entries/A0001-x.md pre-planted as a DANGLING symlink to outside the root (so
Path.exists() is False and create_entry's `already exists` refusal does not fire)."""
import sys, tempfile, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

tmp = Path(tempfile.mkdtemp())
p = make(tmp, git=False)
outside_dir = tmp / "outside"; outside_dir.mkdir()
target_outside = outside_dir / "pwned-entry.md"
assert not target_outside.exists()

symlink_path = p.entries / "A0001-x.md"
os.symlink(target_outside, symlink_path)
print("planted dangling symlink:", symlink_path, "->", os.readlink(symlink_path))
print("path.exists():", symlink_path.exists())

rc = p.cl("new", "x", "--id", "A0001")
print("new --id A0001 rc:", rc)
print("outside file now exists:", target_outside.exists())
if target_outside.exists():
    print("!!! `new` wrote a scaffolded entry OUTSIDE the project root through the dangling symlink")
    print(target_outside.read_text(encoding="utf-8")[:200])
print("check rc:", p.cl("check"))
