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

- 2026-09-08T14:43:44-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/propagate.py § "run" @aadceb0aba82a85fe71b15394896c43977751709
  artifact: 7f7532d47e721ce6ba2629cfe518b085455035e5
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

- 2026-09-11T19:41:48-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" =sha256:8fa19789e9badc1682afa37198032a2207b9e89ef81a5b34d8ec9cfeccb3aa67
  note: re-read after the same commit, which gives this checker a cached mode: it takes the flag and passes it to the entry load. The walk and every rule in it are unchanged.

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
- docs/SCHEMA.md · standing · cites-as-live
- README.md · standing · cites-as-live
