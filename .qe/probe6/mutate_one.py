"""Apply exactly one mutation from sites.json to a fresh copy of src/, then:
  1. run `claims-ledger corpus` against it (fast, no --write paths reachable)
  2. optionally run the pytest unit suite against it, stopping at first failure (-x)

Usage: mutate_one.py <site_index> <sites.json> <pristine_src> <repo_root> <workdir> [--pytest]

Prints one JSON line: {index, module, lineno, kind, text, corpus_caught, corpus_output_tail,
pytest_caught (or null if skipped), pytest_tail}
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

idx = int(sys.argv[1])
sites_path = Path(sys.argv[2]).resolve()
pristine_src = Path(sys.argv[3]).resolve()
repo_root = Path(sys.argv[4]).resolve()
workdir = Path(sys.argv[5]).resolve()
do_pytest = "--pytest" in sys.argv[6:]

sites = json.loads(sites_path.read_text())
site = sites[idx]

mutdir = workdir / f"mut-{idx:03d}"
if mutdir.exists():
    shutil.rmtree(mutdir)
mutdir.mkdir(parents=True)
mut_src = mutdir / "src"
shutil.copytree(pristine_src, mut_src, ignore=shutil.ignore_patterns("__pycache__"))

target = mut_src / "claims_ledger" / site["module"]
lines = target.read_text(encoding="utf-8").splitlines(keepends=True)
start = site["lineno"] - 1
end = site["end_lineno"]  # exclusive slice bound since end_lineno is 1-based inclusive
indent = " " * site["col_offset"]
if site["kind"] == "return-list":
    replacement = f"{indent}return []\n"
else:
    replacement = f"{indent}pass\n"
new_lines = lines[:start] + [replacement] + lines[end:]
target.write_text("".join(new_lines), encoding="utf-8")

env_base = {"PATH": "/usr/bin:/bin", "HOME": str(mutdir), "PYTHONPATH": str(mut_src)}

sanity = subprocess.run(
    [sys.executable, "-c", "import claims_ledger; print(claims_ledger.__file__)"],
    capture_output=True,
    text=True,
    cwd=str(mutdir),
    env=env_base,
    timeout=30,
)
imported_from = sanity.stdout.strip()
if not imported_from.startswith(str(mut_src)):
    raise SystemExit(
        f"SANITY FAILURE: mutant {idx} imported claims_ledger from {imported_from!r}, "
        f"not the mutant tree {mut_src}. PYTHONPATH resolution is broken; every result "
        "from this harness would silently test the pristine package instead of the mutant."
    )

corpus_proc = subprocess.run(
    [sys.executable, "-c", "import sys; from claims_ledger.corpus import run; sys.exit(run.main([]))"],
    capture_output=True,
    text=True,
    cwd=str(mutdir),
    env=env_base,
    timeout=120,
)
corpus_tail = "\n".join(corpus_proc.stdout.strip().splitlines()[-3:])
corpus_caught = corpus_proc.returncode != 0

pytest_caught = None
pytest_tail = ""
if do_pytest:
    pytest_proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-x", "--no-header", str(repo_root / "tests")],
        capture_output=True,
        text=True,
        cwd=str(mutdir),
        env=env_base,
        timeout=300,
    )
    pytest_tail = "\n".join(pytest_proc.stdout.strip().splitlines()[-5:])
    pytest_caught = pytest_proc.returncode != 0

result = {
    "index": idx,
    "module": site["module"],
    "lineno": site["lineno"],
    "kind": site["kind"],
    "text": site["text"],
    "corpus_caught": corpus_caught,
    "corpus_tail": corpus_tail,
    "pytest_caught": pytest_caught,
    "pytest_tail": pytest_tail,
}
print(json.dumps(result))
if "--keep" not in sys.argv[6:]:
    shutil.rmtree(mutdir, ignore_errors=True)
