#!/bin/bash
# Split the fix commit into one patch per hunk and one per file, into $OUT.
# Usage: split.sh <fix-commit> <out-dir>
set -eu
FIX=$1; OUT=$2; REPO=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
rm -rf "$OUT"; mkdir -p "$OUT/hunks" "$OUT/files"
: > "$OUT/hunk-manifest.tsv"
n=0
# `tests/` is excluded on purpose: the experiment holds the test files at HEAD and
# reverts only the fixes, so that a regression going red means it detects the loss of
# its own fix rather than the loss of its own assertions.
for f in $(git -C "$REPO" show --name-only --format= "$FIX" | grep -v "^tests/"); do
  tag=$(echo "$f" | tr '/.' '__')
  git -C "$REPO" show "$FIX" --no-color -- "$f" > "$OUT/files/$tag.patch"
  # One patch per hunk: the file header, plus exactly one @@ block.
  head=$(sed -n '1,/^@@/p' "$OUT/files/$tag.patch" | sed '$d')
  awk -v head="$head" -v out="$OUT/hunks" -v repo="$REPO" -v file="$f" -v man="$OUT/hunk-manifest.tsv" -v start="$n" '
    /^@@/ { i++; fn = out "/" start + i ".patch"; print head > fn; printf "%d\t%s\t%s\n", start + i, file, $0 >> man }
    i > 0 { print >> fn }
    END { print i > "/dev/stderr" }
  ' "$OUT/files/$tag.patch" 2>>"$OUT/counts"
  n=$(wc -l < "$OUT/hunk-manifest.tsv")
done
echo "$n hunks across $(ls "$OUT/files" | wc -l) files"
