#!/bin/bash
# claims-ledger orientation — an agent-harness hook. SessionStart.
#
# The other hooks fire at the moment something is wrong, which is the right place for
# anything that can wait. This one runs before any of that and carries no warnings: it
# hands over the map and the vocabulary — which command answers which question, what the
# statuses and acts are, and where the procedures live — so that a session starts able to
# read what the checkers say rather than having to work it out from a failure.
#
# Counts are asked of the tool, never written down. A tally in prose is false the next
# time an entry lands and nothing checks it.
#
# The hook never blocks: every failure path exits 0 silently.

set -uo pipefail

command -v jq >/dev/null 2>&1 || exit 0

here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd) || exit 0
root=$(cd -- "$here/../.." && pwd) || exit 0

# Silent unless this really is a ledger checkout: the hook ships inside an example
# directory that people copy, and firing in a project with no ledger is noise.
[ -d "$root/ledger/entries" ] || exit 0

python=""
for candidate in "$root/.venv/bin/python" "$root/venv/bin/python" "$(command -v python3 2>/dev/null)"; do
  [ -n "$candidate" ] && [ -x "$candidate" ] || continue
  if "$candidate" -c 'import claims_ledger' >/dev/null 2>&1; then python="$candidate"; break; fi
done
[ -n "$python" ] || exit 0

counts=$(cd "$root" && timeout 20 "$python" -m claims_ledger status 2>/dev/null | tail -1) || true
[ -n "$counts" ] || counts="a ledger under ledger/entries"

jq -cn --arg ctx "This project keeps a claims ledger: $counts. An entry states something the code promises, pinned to the code that keeps it true and cited from the prose that says the same thing in words. \`claims-ledger check\` runs in the pre-commit hook and again in CI, and \`docs/OPERATING.md\` is the authority on running one.

FIVE CHECKERS, each answering a different question. The wording of a finding tells you which one you are holding, and that is what decides the repair:

  validate    is this entry well formed?            frontmatter, sections, verdict lines
  resolve     does every pointer resolve?           'does not resolve', 'has no section'
  references  does a citation match its target?     '<act> against <id>, whose status is ...'
  propagate   are the entry-to-entry edges sound?   'carries no contested verdict by ...'
  freshness   has a pinned ground moved?            'has moved', 'withdrawn', 'unstable pin'

THE VOCABULARY you will be writing in:

  statuses  open · corroborated · contested · refuted · superseded · retracted · non-comparable
            the last four are terminal; contested is not, so an entry can leave it

  acts      cites-as-live       against open or corroborated
            cites-as-contested  against contested
            challenges          against open, corroborated or contested
            cites-as-fallen     against any status at all

A citation names an entry and an act, and the act has to be true of that entry's status as it stands now — \`claims-ledger status\` is what those are. Matching the act to the status is the whole of what a citing sentence promises; there is no status a claim is supposed to end up at.

GROUNDS AND DOCUMENTS are different things. A ground is evidence and can point at any path in the repository. The configured \`documents\` globs decide only where citations are read.

WHERE TO START: the \`tagging-prose-with-claims\` skill for writing entries over a file, \`choosing-a-citation-act\` when an entry's status has moved, \`repair-a-drifted-pin\` when a ground has drifted. Each names the others where they take over." \
  '{hookSpecificOutput:{hookEventName:"SessionStart", additionalContext:$ctx}}'

exit 0
