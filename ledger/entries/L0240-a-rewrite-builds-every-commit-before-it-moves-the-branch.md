---
id: L0240-a-rewrite-builds-every-commit-before-it-moves-the-branch
kind: claim
stated: 2026-09-14T19:13:42-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: ab188d5a8c5ad3d8fedad56f1b121e1c0e900b48a21e526a22a21eadf3f9c5c0
---

## Assertion

A renumber writes every rewritten commit before it moves any ref, so a rewrite that fails part way leaves the branch where it was.

## Scope

metric: the state of the branch after a failed rewrite
cohort: every renumber that does not run to completion
condition: the failure is anything the rewrite reports as a RenumberError

## Grounds

- code: src/claims_ledger/renumber.py § "rewrite" =sha256:a7617476abb94765a512621eceb0ed9dddeeb4729901b20487f9d02f777c9506

## Warrant

rewrite returns the new tip and moves nothing; the ref is moved afterwards by move_branch, so commits written before a failure are unreferenced objects rather than a branch half rewritten.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
