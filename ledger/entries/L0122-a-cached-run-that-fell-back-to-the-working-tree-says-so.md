---
id: L0122-a-cached-run-that-fell-back-to-the-working-tree-says-so
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 04d94ef976a43f16cf50c315973202e2e3c4f764208aa932a00fdd33f5474a35
---

## Assertion

A cached run whose index could not be read says that it fell back to the working tree, and that what is staged was left unchecked.

## Scope

metric: whether the fallback from the index to the working tree is reported
cohort: runs invoked with the cached flag
condition: reading a path from the index fails identically for an unstaged path and an unparsable index

## Grounds

- code: src/claims_ledger/cli.py § "skipped_checks" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395
- code: src/claims_ledger/schema.py § "index_problem" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

skipped_checks asks index_problem whether the index can be read at all, and reports the fallback when it cannot. The two conditions are indistinguishable at the point where the entries are loaded, and the loader takes the first as its answer, so the entries were read — off the working tree. For a pre-commit hook that is a report about something other than what is being committed, which is the one thing the cached mode exists to prevent.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
