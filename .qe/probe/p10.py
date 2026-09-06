import sys, tempfile, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make
tmp = Path(tempfile.mkdtemp()); p = make(tmp, git=False)
paths = []
for slug in ("one","two","three"):
    assert p.cl("new", slug) == 0
for f in sorted(p.entries.glob("*.md")):
    t = f.read_text(encoding="utf-8").replace("metric: TODO","metric: m")
    f.write_text(t, encoding="utf-8"); paths.append(f)
# make the middle one unwritable
os.chmod(paths[1], 0o444)
print("declared shas before:", [f.read_text(encoding='utf-8').split('verbatim_sha: ')[1][:8] for f in paths])
rc = p.cl("sha","--write",*[str(f) for f in paths])
print("rc:", rc)
print("declared shas after :", [f.read_text(encoding='utf-8').split('verbatim_sha: ')[1][:8] for f in paths])
os.chmod(paths[1], 0o644)
