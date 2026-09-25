---
id: L0305-a-number-named-by-hand-is-refused-where-the-repository-holds-it
kind: claim
stated: 2026-09-24T21:41:52-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: eb6c5a1f348487f43a8e43df983c64656ea130d141efaf5cc2ed29a2e10f4417
---

## Assertion

An id named by hand is refused when its number is already held in this checkout, on any ref, or in a sibling worktree, naming the entry that holds it and where, unless the author passes --force.

## Scope

metric: the outcome of claims-ledger new --id
cohort: every mint that names its own id
condition: --force is not given; where git cannot be asked, the number is checked against what could be read and the rest is reported rather than refused

## Grounds

- code: src/claims_ledger/authoring.py § "refuse_a_number_already_held" =sha256:3c86e92976ed14b0bf061be4c8881fb8c2da9dd74a4f6f83ba795c06487b6660
- code: src/claims_ledger/authoring.py § "create_entry" =sha256:4ee432b2278cfd856df56c28cadecc4c61abcc2ff92731782ddf4493b74a7ddd

## Warrant

create_entry calls refuse_a_number_already_held for every named id unless force is set, after the id is known to be well formed and before anything is written; that function compares the A#### prefix, not the whole filename, against this checkout's entries and every id ids_in_the_repository reports, and raises AuthoringError listing each holder with where it was found, so the same number under a different slug cannot pass the way it did when only the path was asked.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
- docs/OPERATING.md · standing · cites-as-live
