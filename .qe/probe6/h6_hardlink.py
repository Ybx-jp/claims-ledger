"""Hypothesis 6: _existing_mode preserves the file's permission bits but write_bytes_
atomically's os.replace swaps in a NEW inode -- any hard link to the old inode now points
at the pre-write content forever. Confirm this happens, and check whether anything in the
project creates or relies on hard links to entries/cache files (grep first; ownership/
ACL/xattr preservation is the same question, code-inspected)."""
import sys, tempfile, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

tmp = Path(tempfile.mkdtemp())
p = make(tmp, git=False)
assert p.cl("new", "a-claim") == 0
a = p.entry("A0001-a-claim.md")
p.write_full_entry(a)

hardlink = tmp / "hardlink-to-a.md"
os.link(a, hardlink)
print("same inode before write:", a.stat().st_ino == hardlink.stat().st_ino)

t = a.read_text(encoding="utf-8")
t = t.replace("cohort: the synthetic graph of these tests", "cohort: edited")
a.write_text(t, encoding="utf-8")
rc = p.cl("sha", "--write", str(a))
print("sha --write rc:", rc)
print("same inode after write:", a.stat().st_ino == hardlink.stat().st_ino)
print("hard link content still the OLD content (broken link):",
      hardlink.read_text(encoding="utf-8") != a.read_text(encoding="utf-8"))
