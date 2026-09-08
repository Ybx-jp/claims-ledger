---
id: L0025-a-propagation-is-recognized-only-on-an-exact-match
kind: claim
stated: 2026-09-07T23:17:47-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 1e5618ee85cb20ffddcf67cda78ac4f61aa0900b87861ff9f15bb3845555f46e
---

## Assertion

An existing verdict discharges a propagation only when its author, its status, its pointer type, its pointer target and its act all match the one owed; a verdict matching some of those leaves the propagation still owed.

## Scope

metric: whether an existing verdict is treated as the propagated verdict for a given cause and act
cohort: verdicts already on an entry when propagate runs
condition: a verdict agreeing with the one owed on some conditions and not on all

## Grounds

- code: src/claims_ledger/propagate.py § "has_propagated" @0af113005f955a4e120d71338993a94cc6efeb7b

## Warrant

has_propagated requires all five conditions of the same verdict, so a contested verdict by another author, one by the propagation author naming a different cause, and one naming the right cause under a different act each fail the test and the run reports the propagation as still missing.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
