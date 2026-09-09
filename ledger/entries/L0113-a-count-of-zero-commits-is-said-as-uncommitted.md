---
id: L0113-a-count-of-zero-commits-is-said-as-uncommitted
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 22cfa545cebc15a8ff14885021d333c597cc732a7cec148d7f285324db82b66c
---

## Assertion

A drift that is still only in the working tree is described as uncommitted rather than as having been touched by zero commits.

## Scope

metric: the wording of the message for a drift the history does not hold
cohort: findings reported before the drift is committed
condition: the pre-commit case is the ordinary one

## Grounds

- code: src/claims_ledger/freshness.py § "since_phrase" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

since_phrase reads a count of zero as the working-tree case and says so. Telling an author that no commits have touched a file they are editing right now reads as a checker that has lost track of its own subject, and the count is for the message rather than for the finding. A count that could not be obtained is reported as unknown rather than guessed at.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
