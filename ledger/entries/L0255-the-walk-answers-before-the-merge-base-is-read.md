---
id: L0255-the-walk-answers-before-the-merge-base-is-read
kind: claim
stated: 2026-09-14T21:04:01-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 250e7f88a1c10239c287c0bfcaddf3b5e270716bb2d90087ef6cca72088e4929
---

## Assertion

A renumber reads the commit walk before it reads the merge base, so a repository it could not walk is not reported as two branches that share no history.

## Scope

metric: which git call decides that a branch cannot be planned
cohort: every plan over a repository whose object store is incomplete
condition: the branch tips resolve; a repository whose tips do not resolve fails earlier

## Grounds

- code: src/claims_ledger/renumber.py § "plan" =sha256:6441d5a08eff4d46321df05ea98f1c6758ffb830f2bb2919338b9fc80a4bc7cc

## Warrant

plan asks rev-list first and raises RepositoryUnreadable when it declines, and only then asks merge-base. Measured on git 2.43.0 with an intermediate commit object removed: merge-base exits 1, which is also its answer for no common ancestor, while rev-list exits 128 — so a merge-base read first turns a broken object store into a statement about history.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
