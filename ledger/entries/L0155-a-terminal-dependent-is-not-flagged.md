---
id: L0155-a-terminal-dependent-is-not-flagged
kind: claim
stated: 2026-09-08T09:39:52-07:00
author: main
grade: measured
supersedes: L0020-a-dependent-that-has-fallen-is-not-flagged
verbatim_change: the Scope metric, cohort and condition now name the terminal statuses rather than the fallen ones, which is the set the checker tests; Backing is unchanged and there is none
verbatim_sha: c44635145721dee2d504a2abf16880ddb50391ca9f22ef00aa2c9da02a4eaa1a
---

## Assertion

A dependent whose own status is terminal is passed over rather than flagged for a live-cited ground that fell, because a verdict after a terminal status would itself be illegal.

## Scope

metric: whether propagate reports or queues anything against a terminal dependent
cohort: entries whose derived status is terminal and which cite a fallen ground cites-as-live
condition: the dependent has reached a terminal status and its ground has fallen

## Grounds

- code: src/claims_ledger/propagate.py § "run" @5ee55ae6992f10c834510759f026644f42614025

## Warrant

run tests the dependent's own status against TERMINAL before the cites-as-live branch and continues the loop, so neither a Report nor a pending block is made against it; the repair for such a dependent is its successor, which the same walk reaches on that successor's own grounds. The test is terminality rather than a fall because the reason the flag is unanswerable is that nothing may follow the status: the predecessor tested FALLEN, so a non-comparable dependent was flagged, and with --write the run appended a verdict validate then refused as one following a terminal verdict.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:44-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/propagate.py § "run" @5ee55ae6992f10c834510759f026644f42614025
  artifact: 7f7532d47e721ce6ba2629cfe518b085455035e5
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

- 2026-09-11T19:41:48-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" =sha256:8fa19789e9badc1682afa37198032a2207b9e89ef81a5b34d8ec9cfeccb3aa67
  note: re-read after the same commit, which gives this checker a cached mode: it takes the flag and passes it to the entry load. The walk and every rule in it are unchanged.

- 2026-09-11T22:04:31-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" =sha256:41d276552f5f6f4ff4d4c194a4fcb58c2ca9d002bffa7d081767f36be10289ea
  note: re-read after the commit answering the fix-review gate on this branch (qe ticket e9b7d35601214a1b). This checker now takes its entries through `entries_for`, so a run that will append decides from the tree it appends to. Every rule this claim is about is untouched; what moved is which tree the list came from when `--write` is on.

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
