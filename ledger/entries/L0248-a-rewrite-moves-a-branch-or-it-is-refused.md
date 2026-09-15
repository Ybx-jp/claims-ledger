---
id: L0248-a-rewrite-moves-a-branch-or-it-is-refused
kind: claim
stated: 2026-09-14T20:20:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 08e5ab9abbfc39112644053d619254e58134b662ae50b171d261e8c7a38b03de
---

## Assertion

A rewrite moves a branch or it is refused; it never moves a detached HEAD.

## Scope

metric: what claims-ledger renumber --write does when the branch does not resolve to a branch
cohort: every renumber asked to write
condition: the ref given resolves to something other than refs/heads/

## Grounds

- code: src/claims_ledger/renumber.py § "branch_ref" =sha256:7a89b9cdd37bee2d37d46e2e146dbd0e7e986d8d79e80f78d2cfbb23c334447f

## Warrant

branch_ref requires the full refname to begin with refs/heads/ and raises otherwise, and cmd_renumber asks it before the rewrite runs; moving a detached HEAD would leave the rewritten commits on no branch, the branch still naming the originals, and the working tree holding the old content with the rewrite staged against it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
