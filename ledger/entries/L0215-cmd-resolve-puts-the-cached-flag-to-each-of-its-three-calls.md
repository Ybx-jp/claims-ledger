---
id: L0215-cmd-resolve-puts-the-cached-flag-to-each-of-its-three-calls
kind: claim
stated: 2026-09-11T15:06:19-07:00
author: main
grade: measured
verbatim_change: assertion narrowed to the three call sites its ground decides, from a claim about which tree every question reaches; Backing unchanged
supersedes: L0214-resolve-asked-for-the-index-reads-it-for-entries-and-artifacts
verbatim_sha: a414ab41c8a530f4c8e0ea18c03294fcde90c7a9317febcff34e2e04baf60f1b
---

## Assertion

The pointer resolver's command passes the cached flag to each of the three calls it makes — the guard, the entry load and the artifact read — rather than to some of them.

## Scope

metric: how many of the three calls cmd_resolve makes are given the cached flag
cohort: every invocation of the resolve command
condition: what each call then does with the flag is that call's own claim, not this one

## Grounds

- code: src/claims_ledger/cli.py § "cmd_resolve" =sha256:39594a29522566db492bfa26b923b0b077c444432e08f8fe3592646715813a13

## Warrant

cmd_resolve names the flag three times, once per call, and the reason to claim that rather than the behaviour it buys is that a partial wiring is the shape a test suite does not catch. Dropping it from the entry load, or from the run, leaves a command answering about a state no commit contains — the working entry against the index's artifact, or the staged entry against the working tree's — and answering it with a pass. Dropping it from the guard is quieter still: the verdict is unchanged and what goes missing is the notice that the index could not be read at all. Measured: before the three tests that hold this, each of the three could be dropped on its own with 1072 tests green. The predecessor claimed instead that the command reads the index for every question it puts to the tree, which is false — a ground pinned at working is read from the working tree whatever the flag says, and under an unreadable index the entries fall back while the artifacts go on asking the index.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-11T17:16:13-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "cmd_resolve" =sha256:657235110311941a207dc508a3b46a9fe8546e3dd135d8ea9e443df2fbce8a16
  note: re-read against the commit that corrects the citing comment beside this section, and the reading carries two corrections to the Warrant above, which is frozen and says them wrong. (i) "and answering it with a pass" states one of two outcomes as though it were the consequence. Measured here, one mutant at a time, against this code: a bare `load_entries` takes `resolve --cached` to exit 0 where 1 was due, checking the tree's corrected entry instead of the staged one whose anchor names nothing — the pass the clause describes, and it is real. A bare `resolve.run` gives both answers: exit 0 on an anchor the index does not hold, and, where the staged entry is the wrong one, exit 1 against the working tree, reporting `names text the working tree does not hold` and advising a restamp of an anchor that was right. A failure about the wrong tree is not a pass and the Warrant does not admit it. What the flag buys is that the answer is about the state being committed at all; a pass is one of the two ways it is not. (ii) "1072 tests green" is the count after these tests were written; the measurement was made at 1069. The claim itself is unchanged and still holds: cmd_resolve names the flag three times, once per call, and the section moved only by the comment. (qe ticket 253184573065433c, QE22-2; the ticket's own note that both mutants exit 1 holds for one of the two shapes, not for the entry load.)

## References
- src/claims_ledger/cli.py · standing · cites-as-live
