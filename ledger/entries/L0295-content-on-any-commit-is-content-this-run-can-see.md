---
id: L0295-content-on-any-commit-is-content-this-run-can-see
kind: claim
stated: 2026-09-20T15:23:32-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9c8a01d091a3e1c53787c336ce270e68bb97ab0facd15357102e60b377e6beba
---

## Assertion

A file some commit of this repository names is reported as held by it, wherever that commit is reachable from.

## Scope

metric: whether a file on a commit outside the current branch is reported as held
cohort: the question whether git already holds a file
condition: the commit naming it is on HEAD, on another ref, or on the incoming side of an operation

## Grounds

- code: src/claims_ledger/schema.py § "committed_paths" =sha256:c7edfaea53cbbb45d45a53598f842719fe0e3e8be90964eaec499d8b42165a96

## Warrant

Every commit passed the gate the pre-commit hook is, so content that is on one has already been checked, and a run that cannot see where it is says no about something that is there. Asked of HEAD alone, the answer was wrong in exactly the state where half of a ledger is elsewhere: during a merge, an entry the incoming side committed is not on HEAD, and reading it as uncommitted both refused the merge and offered to rewrite a frozen region that a commit already names. The reach is therefore every ref and every operation head, and the only remaining no is a file no commit anywhere names.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
