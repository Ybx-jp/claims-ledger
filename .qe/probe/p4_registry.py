import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make
tmp = Path(tempfile.mkdtemp())
p = make(tmp, git=False)
reg = p.root / "ledger" / "sources.jsonl"
raw = reg.read_bytes()
print("registry ends with newline:", raw.endswith(b"\n"))
# a registry whose last line lost its newline
reg.write_bytes(raw.rstrip(b"\n"))
s2 = tmp / "second.txt"; s2.write_text("Another synthetic source.\n", encoding="utf-8")
rc = p.cl("source","add",str(s2),"--id","fx-second","--type","paper","--citation","Second","--authors","B")
print("source add rc:", rc)
print("registry now:")
print(reg.read_text(encoding="utf-8"))
print("lines:", len(reg.read_text(encoding='utf-8').splitlines()))
print("check rc:", p.cl("check"))
