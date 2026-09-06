#!/bin/bash
set -u
F=$1; TAG=$(echo "$F" | tr '/.' '__')
REPO=/home/ybx/code/claims-ledger; W=/tmp/revf/$TAG
rm -rf "$W"; mkdir -p "$W"; git -C "$REPO" archive HEAD | tar -x -C "$W"
git -C "$REPO" show cd19b86 --no-color -- "$F" > /tmp/revf/$TAG.patch 2>/dev/null
if ! (cd "$W" && patch -p1 -R -s --no-backup-if-mismatch -F0 < /tmp/revf/$TAG.patch) 2>/dev/null; then
  echo "{\"file\":\"$F\",\"status\":\"unapplied\"}"; exit 0; fi
LOADED=$(cd "$W" && PYTHONPATH="$W/src" "$REPO/.venv/bin/python" -c "import claims_ledger;print(claims_ledger.__file__)" 2>&1)
case "$LOADED" in "$W"/*) ;; *) echo "{\"file\":\"$F\",\"status\":\"import-broken\"}"; exit 0;; esac
OUT=$(cd "$W" && PYTHONPATH="$W/src" "$REPO/.venv/bin/pytest" -q -p no:cacheprovider -rf \
        $(sed 's|^|tests/|' /tmp/regressions.txt | tr '\n' ' ') 2>&1)
FAILED=$(echo "$OUT" | grep -oE '^FAILED [^ ]+' | sed 's/FAILED //' | tr '\n' ',')
echo "{\"file\":\"$F\",\"status\":\"ran\",\"failed\":\"$FAILED\",\"summary\":\"$(echo "$OUT"|tail -1|tr -d '"')\"}"
