#!/bin/bash
# claims-ledger status guard — an agent-harness hook. PostToolUse, matcher Edit|Write|MultiEdit.
#
# `pin-guard.sh` watches the ground; this watches the citation. They are different
# failures with different repairs, and conflating them is the mistake this exists to stop.
#
# When an entry's status moves — a drift contests it, a ground it cites falls, a person
# refutes it — every sentence citing it under an act that status does not allow becomes a
# false sentence, and `references` says so by name. The finding is precise and the repair
# is a judgement, and an agent reading it under time pressure reliably makes the same
# wrong move: it treats `contested` as an emergency and reaches for a supersession, which
# is the most expensive of four legitimate outcomes and usually not the right one.
#
# So this hook does one thing: when `references` objects to an act against a status, it
# names the four outcomes and leaves the choice where it belongs. It never chooses, and it
# never writes.
#
# Throttled on the digest of the finding, so an unchanged objection is reported once and a
# NEW one still speaks. Nothing here is repository-specific: the interpreter is discovered
# and the ledger is asked about itself.
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

path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -n "$path" ] || exit 0

# Derived from this script's own location rather than from `cwd`, so a copy living in a
# scratch worktree guards that worktree. Adjust the number of `..` if you move it.
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd) || exit 0
root=$(cd -- "$here/../.." && pwd) || exit 0

case "$path" in
  "$root"/*) ;;
  *) exit 0 ;;
esac

# An interpreter plus `-m`, never the `claims-ledger` console script: a console script in
# a virtualenv that is not active is not on PATH, and the hook would fail on every firing.
python=""
for candidate in "$root/.venv/bin/python" "$root/venv/bin/python" "$(command -v python3 2>/dev/null)"; do
  [ -n "$candidate" ] && [ -x "$candidate" ] || continue
  if "$candidate" -c 'import claims_ledger' >/dev/null 2>&1; then python="$candidate"; break; fi
done
[ -n "$python" ] || exit 0

state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/claims-ledger/status-guard"
state_file="$state_dir/$session"

fired() { [ -f "$state_file" ] && grep -qxF "$1" "$state_file" 2>/dev/null; }
remember() { mkdir -p "$state_dir" 2>/dev/null && printf '%s\n' "$1" >> "$state_file" 2>/dev/null || true; }

# Read-only. Whether an act is legal against a status is `references`' question and is
# asked of the package rather than reimplemented here; a hook that restated ACT_ALLOWS
# would drift from the checker it serves.
finding=$(cd "$root" && timeout 20 "$python" -m claims_ledger references 2>&1) || true
[ -n "$finding" ] || exit 0

# Only the act-vs-status shape. Every other `references` failure — a dangling id, a
# one-way reference, an Assertion carried verbatim — has its own repair and is left to the
# checker's own words at commit time.
mismatch=$(printf '%s\n' "$finding" | grep -E 'against .*, whose status is ' || true)
[ -n "$mismatch" ] || exit 0

key="act:$(printf '%s' "$mismatch" | cksum | tr -d ' ')"
fired "$key" && exit 0
remember "$key"

jq -cn --arg ctx "claims-ledger status guard: a citing sentence names an entry under an act its current status does not allow.

$mismatch

This is \`references\`, not \`freshness\`. Re-pinning answers nothing here — the entry's STATUS is what the sentence is wrong about. There are four honest outcomes and the checkers accept all four; choose by what is true, not by what is cheapest to make green:

  1. Flip the act. If the entry is contested and the prose should say so, change the citation to \`cites-as-contested\` AND the matching row in the entry's ## References. A contested claim visibly cited as contested is a correct ledger, not a holding pattern. \`cites-as-fallen\` is legal against any status.
  2. Supersede — the claim still holds on the artifact as it now stands. docs/OPERATING.md has the sequence. Costs an entry, a verdict and every citation moved.
  3. Let it fall — append a refuted or retracted verdict and rewrite the prose.
  4. Corroborate — ONLY if you have just re-read the artifact and it still supports the Assertion. A corroborating verdict you did not earn is a false statement no checker can catch, and it silences the ground permanently.

Never delete the citation to make the check pass: that passes by removing the thing being checked." \
  '{hookSpecificOutput:{hookEventName:"PostToolUse", additionalContext:$ctx}}'

exit 0
