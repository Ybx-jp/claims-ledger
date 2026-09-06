#!/bin/bash
# Revert exactly one hunk of cd19b86 in a clean copy of the tree, then run the 31
# regressions the fifth pass flipped. Prints one JSON line.
set -u
H=$1
REPO=/home/ybx/code/claims-ledger
W=/tmp/rev/$H
rm -rf "$W"; mkdir -p "$W"
git -C "$REPO" archive HEAD | tar -x -C "$W"
if ! (cd "$W" && patch -p1 -R -s --no-backup-if-mismatch -F0 < /tmp/hunks/$H.patch) 2>/tmp/rev/$H.patcherr; then
  echo "{\"hunk\":\"$H\",\"status\":\"unapplied\"}"; exit 0
fi
# The copy must be the module under test, not the editable install pointing at the checkout.
LOADED=$(cd "$W" && PYTHONPATH="$W/src" "$REPO/.venv/bin/python" -c "import claims_ledger;print(claims_ledger.__file__)" 2>&1)
case "$LOADED" in "$W"/*) ;; *) echo "{\"hunk\":\"$H\",\"status\":\"wrong-module\",\"loaded\":\"$LOADED\"}"; exit 0;; esac
OUT=$(cd "$W" && PYTHONPATH="$W/src" "$REPO/.venv/bin/pytest" -q -p no:cacheprovider \
        --ignore=tests/test_pass6_regressions.py -rf \
        $(sed 's|^|tests/|;s|tests/tests/|tests/|' /tmp/regressions.txt | tr '\n' ' ') 2>&1)
FAILED=$(echo "$OUT" | grep -oE '^FAILED [^ ]+' | sed 's/FAILED //' | tr '\n' ',')
SUMMARY=$(echo "$OUT" | tail -1)
echo "{\"hunk\":\"$H\",\"status\":\"ran\",\"failed\":\"$FAILED\",\"summary\":\"$(echo $SUMMARY | tr -d '\"')\"}"
