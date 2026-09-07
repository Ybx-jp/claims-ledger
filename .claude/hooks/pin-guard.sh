#!/bin/bash
# claims-ledger pin guard — PostToolUse, matcher Edit|Write|MultiEdit.
#
# This repository's prose is pinned to its own code, and two failures follow from that
# arrangement rather than from any bug:
#
#   1. An edit lands inside a pinned section and nothing says so until `git commit`,
#      by which point the edit is finished and its author has moved on. `freshness`
#      answers in ~0.14s, so the answer can be had at edit time instead.
#   2. A design commitment gets written into a README sentence or a docstring with no
#      entry behind it. No checker can catch this — `references` only checks citations
#      that were actually written — so it is the one place a reminder is the mechanism.
#
# Both classes are throttled, because an always-on reminder is wallpaper. (1) is keyed on
# the digest of the finding, so unchanged drift is reported once and NEW drift still
# speaks; (2) is keyed once per session, on the first qualifying edit.
#
# The hook never blocks: every failure path exits 0 silently. A guard that can break the
# session is worse than no guard.

set -uo pipefail

command -v jq >/dev/null 2>&1 || exit 0
input=$(cat) || exit 0

event=$(printf '%s' "$input" | jq -r '.hook_event_name // empty' 2>/dev/null) || exit 0
[ "$event" = "PostToolUse" ] || exit 0

session=$(printf '%s' "$input" | jq -r '.session_id // empty' 2>/dev/null)
[ -n "$session" ] || exit 0

# `file_path` for Edit/Write; MultiEdit carries the same key.
path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -n "$path" ] || exit 0

# The root is derived from this script's own location rather than from `cwd`, which is
# wherever the session happens to be, and rather than from $CLAUDE_PROJECT_DIR alone, so
# that a copy of this hook running inside a scratch worktree guards that worktree.
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd) || exit 0
root=$(cd -- "$here/../.." && pwd) || exit 0

case "$path" in
  "$root"/*) rel=${path#"$root"/} ;;
  *) exit 0 ;;
esac

python="$root/.venv/bin/python"
[ -x "$python" ] || exit 0

state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/claims-ledger/pin-guard"
state_file="$state_dir/$session"

fired() { [ -f "$state_file" ] && grep -qxF "$1" "$state_file" 2>/dev/null; }
remember() { mkdir -p "$state_dir" 2>/dev/null && printf '%s\n' "$1" >> "$state_file" 2>/dev/null || true; }
emit() { jq -cn --arg ctx "$1" \
  '{hookSpecificOutput:{hookEventName:"PostToolUse", additionalContext:$ctx}}'; }

# --- class drift: measured, re-fires when the finding changes -------------------------
# Read-only. `--write` is a judgement about the ledger and belongs to the session, never
# to a hook firing behind the author's back.
finding=$(cd "$root" && timeout 15 "$python" -m claims_ledger freshness 2>&1) || true
if [ -n "$finding" ] && ! printf '%s' "$finding" | grep -q '0 failure(s), 0 flag(s)'; then
  key="drift:$(printf '%s' "$finding" | cksum | tr -d ' ')"
  if ! fired "$key"; then
    remember "$key"
    emit "claims-ledger pin guard: an edit in this repository has drifted a pinned ground.

$finding

The pins are what hold the README and the docstrings to the code. Repair them in this session rather than at \`git commit\`, where the pre-commit hook will refuse the commit anyway. The procedure — including the parts that cannot be undone once committed — is the \`repair-a-drifted-pin\` skill. Do not delete a verdict or edit a ground to make the checker pass."
    exit 0
  fi
fi

# --- class newclaim: once per session, on a document the checkers read ----------------
case "$rel" in
  README.md|CHANGELOG.md|pyproject.toml) ;;
  docs/*.md) case "${rel#docs/}" in */*) exit 0 ;; esac ;;
  src/claims_ledger/*.py) case "${rel#src/claims_ledger/}" in */*) exit 0 ;; esac ;;
  *) exit 0 ;;
esac

if ! fired newclaim; then
  remember newclaim
  emit "claims-ledger pin guard (once per session): you just edited $rel, one of the documents the ledger reads.

If this edit states a NEW commitment about what the package does — a README sentence or a docstring that a reader would take as a promise — it needs an entry under \`ledger/\`, pinned to the code that keeps it true and cited from the sentence. No checker can find this for you: \`references\` only checks citations that were actually written, so prose that quietly asserts something and cites nothing passes every check and is exactly the drift this ledger exists to prevent.

Adding one takes two commits and the pre-commit hook will refuse the first; see CLAUDE.md. If the edit states no new commitment, ignore this."
fi

exit 0
