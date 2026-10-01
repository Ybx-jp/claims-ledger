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

An id named by hand is refused when its number is already held in this checkout or in a sibling worktree, or was ever added on any ref, naming the entry that took it and where, unless the author passes --force.

## Scope

metric: the outcome of claims-ledger new --id
cohort: every mint that names its own id
condition: --force is not given; where git cannot be asked, the number is checked against what could be read and the rest is reported rather than refused

## Grounds

- code: src/claims_ledger/authoring.py § "refuse_a_number_already_held" =sha256:2654e166880cf9d50ee46f196464f7a021640245e62502bdaece8d106cf16e9b
- code: src/claims_ledger/authoring.py § "create_entry" =sha256:4b1adf6290657ebbe69a40bd6d2cad7d1545a9c3a919df3f3bd2f1e78a6ff886
- code: src/claims_ledger/authoring.py § "ids_in_the_repository" =sha256:4e7df389c60d7e37c887c2ffd97348e80790d68dc451e9b1c7f867970a277f18

## Warrant

create_entry calls refuse_a_number_already_held for every named id unless force is set, after the id is known to be well formed and before anything is written; that function compares the A#### prefix, not the whole filename, against this checkout's entries and every id ids_in_the_repository reports, and raises AuthoringError listing each holder with where it was found, so the same number under a different slug cannot pass the way it did when only the path was asked. ids_in_the_repository is where the other two places are read: a walk of every ref for each entry file a commit added, naming the ref that commit was reached on, and the entries directory of each sibling worktree git lists, naming that worktree.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
- docs/OPERATING.md · standing · cites-as-live
