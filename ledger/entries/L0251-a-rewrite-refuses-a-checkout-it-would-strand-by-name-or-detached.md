---
id: L0251-a-rewrite-refuses-a-checkout-it-would-strand-by-name-or-detached
kind: claim
stated: 2026-09-14T20:20:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: a68628b5fd4fe4cd6db3bf39c1d874da7b5df176f1f2d8a6a7a9062f4dd7bc6d
---

## Assertion

A rewrite is refused when another checkout holds the branch by name or sits detached on a commit the rewrite would replace.

## Scope

metric: what a renumber does when a sibling checkout would be stranded
cohort: every linked worktree of the repository
condition: the worktree names the branch, or its HEAD is one of the commits being replaced

## Grounds

- code: src/claims_ledger/renumber.py § "checkout_holding" =sha256:d51e7800e3575adc7e3dc5b53a3f8c5e5284c11e6c6be95f7bd64795dbbfffe3

## Warrant

checkout_holding reads every record git worktree list prints, treats a matching branch line and a detached HEAD among the replaced commits alike, and returns the first such checkout that is not this one; a scan that stopped at the first match would always stop at this checkout, which is the one being reset rather than the one being stranded.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
