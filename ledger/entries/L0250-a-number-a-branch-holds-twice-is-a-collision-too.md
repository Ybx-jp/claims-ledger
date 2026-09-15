---
id: L0250-a-number-a-branch-holds-twice-is-a-collision-too
kind: claim
stated: 2026-09-14T20:20:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 98c84e8cefc4c7cbdd262688c4a6b659e49399417fd0cace3d94200e930d054a
---

## Assertion

A number a branch holds twice is renumbered by the same command as one the receiving side holds, with the earliest id in sort order keeping the number.

## Scope

metric: which ids a renumber plans to move
cohort: every branch carrying two entries under one number
condition: both entries are introduced by the branch rather than inherited from its base

## Grounds

- code: src/claims_ledger/renumber.py § "plan" =sha256:e131100d1b0f8424d513f2f299f7d58bd6fdc8f5db8b0a87d5cfa45e45a58254

## Warrant

plan unions the ids whose number the receiving side holds with the ids the branch itself repeats, keeping the first in sort order and moving the rest; check_numbers names this command for a duplicated number without asking where the duplicate came from, so the command answers for both shapes.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
