#!/bin/bash
# Reverse-apply exactly one patch to a clean copy of the tree at HEAD, then run this
# pass's regressions against it. The test files stay at HEAD throughout, so a regression
# going red means the flipped test really detects the loss of its own fix.
# Usage: run_one.sh <patch> <label>   — prints one JSON line.
set -u
PATCHFILE=$1; LABEL=$2
REPO=${REPO:-/home/ybx/code/claims-ledger}
W=$(mktemp -d "${TMPDIR:-/tmp}/rev7-XXXXXX")
trap 'rm -rf "$W"' EXIT
git -C "$REPO" archive HEAD | tar -x -C "$W"
if ! (cd "$W" && patch -p1 -R -s --no-backup-if-mismatch -F0 < "$PATCHFILE") 2>/dev/null; then
  echo "{\"label\":\"$LABEL\",\"status\":\"unapplied\"}"; exit 0
fi
# The copy must be the module under test, not the editable install pointing at the checkout.
LOADED=$(cd "$W" && PYTHONPATH="$W/src" "$REPO/.venv/bin/python" -c "import claims_ledger;print(claims_ledger.__file__)" 2>&1)
case "$LOADED" in "$W"/*) ;; *) echo "{\"label\":\"$LABEL\",\"status\":\"import-broken\"}"; exit 0;; esac
OUT=$(cd "$W" && PYTHONPATH="$W/src" "$REPO/.venv/bin/pytest" -q -p no:cacheprovider -p no:randomly -rf \
        $(tr '\n' ' ' < "$REPO/.qe/probe7/revert-experiment/regressions.txt") 2>&1)
FAILED=$(echo "$OUT" | grep -oE '^FAILED [^ ]+' | sed 's/FAILED //' | tr '\n' ',')
# The corpus is a gate of its own — it is what the release workflow runs against the
# built wheel — and a seed is a regression like any other. A pytest-only sweep would
# report a seed that detects nothing as a hunk that nothing detects.
CORPUS=$(cd "$W" && PYTHONPATH="$W/src" "$REPO/.venv/bin/python" -m claims_ledger corpus 2>&1 | tail -1)
echo "{\"label\":\"$LABEL\",\"status\":\"ran\",\"failed\":\"$FAILED\",\"corpus\":\"$(echo "$CORPUS" | tr -d '\"')\",\"summary\":\"$(echo "$OUT" | tail -1 | tr -d '"')\"}"
