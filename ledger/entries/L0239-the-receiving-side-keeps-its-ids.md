---
id: L0239-the-receiving-side-keeps-its-ids
kind: claim
stated: 2026-09-14T19:13:42-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 65e882b80b8c734eb09079ddd82e6d4cf3d2db21676ac34efa27da0aeab9ab13
---

## Assertion

A renumber moves the ids of the branch being merged and never those of the branch being merged into.

## Scope

metric: which side of a collision a renumber rewrites
cohort: every pair of branches holding one number
condition: a renumber is asked for, naming the branch and what it would merge into

## Grounds

- code: src/claims_ledger/renumber.py § "plan" =sha256:e030be0a73304cfe39ba7ff91c0fece383cbc63fa210fca24fba4ef453e1def7

## Warrant

plan takes the numbers the receiving commit holds as fixed and maps only the ids the branch introduces, so the direction is decided by which branch is being merged rather than by any ordering of the two, and three open branches are three sequential merges rather than a question needing an arbiter.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
