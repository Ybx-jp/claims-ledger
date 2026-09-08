---
id: L0107-presence-is-asked-of-stat-rather-than-of-is-file
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 68ab8eafdf3a1bc40667397341693ef89f8952937fb9bfac4f3f5615684cfab7
---

## Assertion

Whether an artifact is still present is asked of stat directly, because a file test has two answers where three are needed.

## Scope

metric: how presence is established, and what an unsearchable directory produces
cohort: evidence artifacts read from the working tree
condition: interpreter versions differ in how they report a permission error here

## Grounds

- code: src/claims_ledger/freshness.py § "in_this_run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

in_this_run calls os.stat and separates three outcomes: gone, present as a regular file, and could not be reached. The convenience test collapses the third into one of the first two, and does it differently by version — one raises the permission error out of the checker, which printed nothing and omitted a whole checker from the summary, and another swallows it and answers no, which is a confident report that a file nobody could look at had been withdrawn. A directory or a FIFO where the artifact was is also not an artifact to read, and that is established here rather than guessed at.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
