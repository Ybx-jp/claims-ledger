#!/bin/bash
# claims-ledger orientation — an agent-harness hook. SessionStart.
#
# The other two hooks fire at the moment of the mistake, which is the right place for
# anything that can wait. This one carries only what an agent needs *before* it acts, and
# is deliberately short: an orientation nobody finishes reading is wallpaper, and the
# house rule for these hooks is that a reminder which fires constantly is worse than none.
#
# What is here is the small set of things measured to be got wrong on a first encounter,
# each of which sends the work in a wrong direction that later hooks cannot recall:
#
#   - which checker owns which failure, because repairing the wrong one is silent waste;
#   - that `documents` gates citations and never grounds, because the opposite belief
#     makes whole classes of claim look impossible to ground;
#   - that `cites-as-live` is not a goal, because believing it turns every contested
#     entry into an emergency supersession.
#
# Everything else is left to the skills and to docs/OPERATING.md, which is the authority.
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

# The live counts, asked of the ledger rather than written down. A tally in prose is false
# the next time an entry lands, which is the one thing this hook must not become.
counts=$(cd "$root" && timeout 20 "$python" -m claims_ledger status 2>/dev/null | tail -1) || true
[ -n "$counts" ] || counts="a ledger under ledger/entries"

jq -cn --arg ctx "claims-ledger is self-hosted in this repository: $counts. \`claims-ledger check\` runs in the pre-commit hook and again in CI. docs/OPERATING.md is the authority on running it; read it before repairing anything.

Three things that are got wrong on a first encounter, and that later warnings cannot undo:

1. WHICH CHECKER OWNS WHAT. \`validate\` holds one entry's shape and wording. \`resolve\` holds that pointers resolve. \`references\` holds a citation's ACT against its target's current STATUS. \`propagate\` walks entry-to-entry edges. \`freshness\` compares a ground's bytes against its pin. A message naming an act and a status is \`references\`, and re-pinning will not answer it; a message saying a section has moved is \`freshness\`, and rewriting a sentence will not answer that.

2. \`documents\` GATES CITATIONS, NEVER GROUNDS. The configured document globs decide only where citations are read. A \`code:\` or \`toml:\` ground resolves any path in the repository. 'This file is not a document' never means 'a claim about this code cannot be grounded'.

3. \`cites-as-live\` IS NOT THE GOAL. Every claim needs an HONEST status, and the citing sentence must match it. The acts are \`cites-as-live\` (open, corroborated), \`cites-as-contested\` (contested), \`challenges\` (open, corroborated, contested) and \`cites-as-fallen\` (any status). A contested entry cited as contested is a correct ledger. Do not reach for a supersession to make a checker green.

Skills: use \`tagging-prose-with-claims\` BEFORE writing a batch of entries over a file — citation placement has to be decided first, and getting it wrong costs a supersession per claim already pinned there. Use \`choosing-a-citation-act\` when an entry's status has moved. Use \`repair-a-drifted-pin\` when a ground has drifted." \
  '{hookSpecificOutput:{hookEventName:"SessionStart", additionalContext:$ctx}}'

exit 0
