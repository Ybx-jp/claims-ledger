---
id: L0020-a-dependent-that-has-fallen-is-not-flagged
kind: claim
stated: 2026-09-07T23:17:46-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 12748682289351ad78e2dd7a2cd9618d59695455cc861b0285a9f65191c5e6e5
---

## Assertion

A dependent whose own status has fallen is passed over rather than flagged for a live-cited ground that fell, because a verdict after a terminal status would itself be illegal.

## Scope

metric: whether propagate reports or queues anything against a fallen dependent
cohort: entries whose derived status is refuted, superseded or retracted and which cite a fallen ground cites-as-live
condition: both the dependent and its ground have fallen

## Grounds

- code: src/claims_ledger/propagate.py § "run" @0af113005f955a4e120d71338993a94cc6efeb7b

## Warrant

run tests the dependent's own status against FALLEN before the cites-as-live branch and continues the loop, so neither a Report nor a pending block is made against it; the repair for such a dependent is its successor, which the same walk reaches on that successor's own grounds.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
