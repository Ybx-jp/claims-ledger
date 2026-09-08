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

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
