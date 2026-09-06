import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make
tmp = Path(tempfile.mkdtemp())
p = make(tmp, git=False)
assert p.cl("new", "a-claim") == 0
path = p.entry("A0001-a-claim.md")
p.write_full_entry(path)
p.git("init","-q"); p.git("add","-A"); p.git("commit","-qm","committed LF")
print("check:", p.cl("check"))
raw = path.read_bytes()
# convert ONLY the frozen region to CRLF
head, sep, tail = raw.partition(b"<!-- APPEND BELOW THIS LINE ONLY -->")
path.write_bytes(head.replace(b"\n", b"\r\n") + sep + tail)
print("frozen region rewritten to CRLF; check:", p.cl("check"))
