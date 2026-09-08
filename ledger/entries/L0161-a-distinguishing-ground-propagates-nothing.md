---
id: L0161-a-distinguishing-ground-propagates-nothing
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 1d9b88a016f3f067454504fe10f8e9310dc9620760f4248723869aac1f0f390e
---

## Assertion

An entry that distinguishes itself from another entry is passed over when that other entry falls, with nothing reported and nothing appended.

## Scope

metric: whether propagate reports or queues anything for a distinguishes ground
cohort: entries carrying a distinguishes ground whose target has fallen
condition: the target has reached a fallen status

## Grounds

- code: src/claims_ledger/propagate.py § "run" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

run branches on cites-as-live and on challenges and on nothing else, so an act outside those two carries no edge for the walk to follow. That is the intended reading rather than an omission: what propagates is a dependence, and a distinction is the statement that there is none. The target's fall is news about the target, and about an entry that rested on it; it is not news about an entry whose Warrant said the two were different claims.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
- docs/SCHEMA.md · standing · cites-as-live
- README.md · standing · cites-as-live
