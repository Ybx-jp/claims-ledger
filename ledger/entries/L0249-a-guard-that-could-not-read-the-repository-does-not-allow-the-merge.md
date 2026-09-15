---
id: L0249-a-guard-that-could-not-read-the-repository-does-not-allow-the-merge
kind: claim
stated: 2026-09-14T20:20:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 14d730a00ca34363b1fb999674a702b4be95e809cc213985d89f17174b724220
---

## Assertion

A merge guard that could not read the repository refuses the merge rather than allowing it.

## Scope

metric: the exit code of renumber --on-merge when a git question is declined
cohort: every merge a guard asks about
condition: the repository could not be read; a branch that merely cannot be planned is a different answer

## Grounds

- code: src/claims_ledger/renumber.py § "RepositoryUnreadable" =sha256:a743684e6d0cb0e15e7b50cc0290d03601bb7fe213bb7ab21681afc157c2da39
- code: src/claims_ledger/cli.py § "cmd_renumber" =sha256:ec5f0e891c15fe6919ab2825976b488dc830b60974ef6cf38b6f859435750916

## Warrant

RepositoryUnreadable is raised where ids_in_the_repository reports a declined question and is caught separately in cmd_renumber, which returns non-zero under --on-merge; every other RenumberError returns zero there, because a branch the guard cannot plan is not its business while a repository it could not read is the one state in which it knows nothing.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
- src/claims_ledger/cli.py · standing · cites-as-live
