#!/bin/bash
# claims-ledger orientation — an agent-harness hook. SessionStart.
#
# The other hooks fire when something is wrong, which is the right place for anything that
# can wait. This one runs first and carries the map: which command answers which question,
# what the vocabulary is and where to print it, and which skill takes over for which
# finding. A session that has it reads a finding instead of deciphering one.
#
# Everything variable is asked of the installed package rather than written here — the
# counts, the evidence types this project configures, the statuses. A tally or a table in
# prose is wrong as soon as the project changes and nothing checks it.
#
# The hook never blocks: every failure path exits 0 silently.

set -uo pipefail

command -v jq >/dev/null 2>&1 || exit 0

here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd) || exit 0
root=$(cd -- "$here/../.." && pwd) || exit 0

# Silent unless this really is a ledger checkout: the hook ships inside an example
# directory that people copy, and firing in a project with no ledger is noise.
[ -d "$root/ledger/entries" ] || exit 0

# An interpreter plus `-m`, never the `claims-ledger` console script: a console script in a
# virtualenv that is not active is not on PATH, and the hook would fail on every firing.
python=""
for candidate in "$root/.venv/bin/python" "$root/venv/bin/python" "$(command -v python3 2>/dev/null)"; do
  [ -n "$candidate" ] && [ -x "$candidate" ] || continue
  if "$candidate" -c 'import claims_ledger' >/dev/null 2>&1; then python="$candidate"; break; fi
done
[ -n "$python" ] || exit 0

counts=$(cd "$root" && timeout 20 "$python" -m claims_ledger status 2>/dev/null | tail -1) || true
[ -n "$counts" ] || counts="a ledger under ledger/entries"

# What a claim may rest on is per project, so it is asked rather than assumed. A ledger
# over source configures different types from one over papers or design documents.
kinds=$(cd "$root" && timeout 20 "$python" -c \
  'from claims_ledger import open_ledger; print(", ".join(open_ledger().config.evidence_types))' 2>/dev/null) || true
[ -n "$kinds" ] || kinds="see the project configuration"

jq -cn --arg counts "$counts" --arg kinds "$kinds" --arg ctx "This project keeps a claims ledger: __COUNTS__. An entry states one thing the project is answerable for, grounded in the artifact that makes it true and cited from the prose that says the same thing in words. This project's grounds may name: __KINDS__. \`claims-ledger check\` runs in the pre-commit hook and again in CI.

SIX COMMANDS ANSWER DIFFERENT QUESTIONS, and the wording of a finding says which one you are holding — that is what decides the repair.

  claims-ledger status       what every entry is, and the status it derives to right now
  claims-ledger validate     is each entry well formed?           frontmatter, sections, verdicts
  claims-ledger resolve      does every pointer resolve?          'does not resolve', 'has no section'
  claims-ledger references   does a citation match its target?    '<act> against <id>, whose status is ...'
  claims-ledger propagate    are the entry-to-entry edges sound?
  claims-ledger freshness    has a pinned ground changed?         'has moved', 'withdrawn', 'unstable pin', 'unknown'

\`claims-ledger --help\` lists them all and \`claims-ledger <command> --help\` its options. The package is importable, and exports its own vocabulary rather than asking you to remember it:

  python -c 'from claims_ledger import STATUSES, ACTS, GRADES, KINDS; print(STATUSES, ACTS)'

TWO THINGS TO HAVE STRAIGHT. A citation names an entry and an act, and the act has to be true of that entry's status as it stands — matching them is the whole of what a citing sentence promises. And a ground is evidence that can name any path the project holds, while the configured document globs decide only where citations are read.

WHERE TO GO. \`tagging-prose-with-claims\` to turn prose into entries. \`choosing-a-citation-act\` for a finding naming an act and a status. \`repair-a-drifted-pin\` for a moved, withdrawn, unstable or unknown ground — including the case where the artifact moved and the claim is untouched, which is acknowledged rather than superseded. Each skill carries a reference/ directory with the detail." \
  '{hookSpecificOutput:{hookEventName:"SessionStart",
    additionalContext:($ctx | sub("__COUNTS__"; $counts) | sub("__KINDS__"; $kinds))}}'

exit 0
