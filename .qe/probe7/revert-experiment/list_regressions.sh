#!/bin/bash
# The regressions this pass added or flipped, as pytest node ids: every test in
# tests/test_pass6_regressions.py, plus every `def test_` this pass's fix commit added to
# any other test file. Written to regressions.txt beside this script.
set -eu
REPO=$(git rev-parse --show-toplevel); OUT="$REPO/.qe/probe7/revert-experiment/regressions.txt"
BASE=${1:-HEAD~1}
{
  "$REPO/.venv/bin/python" - <<'PY'
import ast, pathlib
p = pathlib.Path("tests/test_pass6_regressions.py")
for n in ast.parse(p.read_text()).body:
    if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"):
        print(f"{p}::{n.name}")
PY
  git diff -U0 "$BASE" -- 'tests/*.py' ':!tests/test_pass6_regressions.py' \
    | awk '/^\+\+\+ b\//{f=substr($2,3)} /^\+def test_/{sub(/^\+def /,""); sub(/\(.*/,""); print f "::" $0}'
} | sort -u > "$OUT"
wc -l < "$OUT"
