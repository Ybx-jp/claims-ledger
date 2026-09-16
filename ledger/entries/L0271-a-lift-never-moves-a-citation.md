---
id: L0271-a-lift-never-moves-a-citation
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: ccd1390ae78f9a36c1dadc1e4b3c11c269ba6f9108088d5f30dde5bae9f31795
---

## Assertion

A lift never takes a line carrying a citation, of the entry it is lifting for or of any other.

## Scope

metric: which lines a lift may take
cohort: the lines of a docstring body inside a pinned section
condition: a section pinned by more than one entry

## Grounds

- code: src/claims_ledger/lift.py § "liftable" =sha256:7360a696fa36f08b3acee31551973e2b3d8a12729c63993fed2dcdaa9a10d619

## Warrant

Sections are often pinned by several entries, each citing from the same docstring. A lift that took their citations would move them where no configured document glob reaches and leave their References rows naming a file that no longer cites them — a silent detection regression that every checker would pass. A citation line therefore ends one run of liftable prose and begins the next.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/lift.py · standing · cites-as-live
