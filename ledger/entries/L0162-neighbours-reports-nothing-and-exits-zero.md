---
id: L0162-neighbours-reports-nothing-and-exits-zero
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: c3d4cd0e5f7b4869af56c2c7bd7a4246b8dd34a7848209473c686509c3882822
---

## Assertion

The neighbours lookup returns lines of text rather than reports, writes to nothing, exits zero whatever it finds, and sits outside the checker list that check iterates.

## Scope

metric: the reports built, the files written, the exit code, and membership of the checker list
cohort: the neighbours command
condition: every ledger it can open

## Grounds

- code: src/claims_ledger/neighbours.py § "run" @aadceb0aba82a85fe71b15394896c43977751709
- code: src/claims_ledger/cli.py § "cmd_neighbours" @aadceb0aba82a85fe71b15394896c43977751709
- code: src/claims_ledger/cli.py § "CHECKERS" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

run returns lines of text and constructs no Report, cmd_neighbours returns 0 on every path but the usage error of a target that names nothing, and CHECKERS lists the five checkers without it, which is the list check iterates. The exit code of every other command here answers whether the ledger is sound; this one has no answer to that question, and a lookup that reported somebody should read these two would be a gate wearing a lookup's name. The same heuristic run over the whole ledger at once names a few hundred pairs to surface the two worth reading, and a gate at that rate is worse than none because it teaches its readers to pass it by.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T13:37:41-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/neighbours.py § "run" @aadceb0aba82a85fe71b15394896c43977751709
  artifact: 578965068168528d1b774ed9ee534ec489450263
  note: propagated from a moved ground

- 2026-09-08T13:55:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/neighbours.py § "run" @989493fa4655725014cedb6408b4ff9c7e680498
  note: read against the change in commit 989493f, which made run append the ground line the answer hands over; it still builds no Report, writes nothing and returns without an exit code of its own, which is what this claim names
- 2026-09-08T14:43:44-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "CHECKERS" @aadceb0aba82a85fe71b15394896c43977751709
  artifact: 70593c15b5bc7b0d9c71b393eb5f7f5e1829e29b
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "CHECKERS" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

## References

- src/claims_ledger/neighbours.py · standing · cites-as-live
- src/claims_ledger/cli.py · standing · cites-as-live
- README.md · standing · cites-as-live
