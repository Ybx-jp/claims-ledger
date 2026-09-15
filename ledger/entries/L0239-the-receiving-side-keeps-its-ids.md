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

- 2026-09-14T20:21:10-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/renumber.py § "plan" =sha256:e030be0a73304cfe39ba7ff91c0fece383cbc63fa210fca24fba4ef453e1def7
  artifact: sha256:e131100d1b0f8424d513f2f299f7d58bd6fdc8f5db8b0a87d5cfa45e45a58254
  note: propagated from a moved ground

- 2026-09-14T20:21:11-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/renumber.py § "plan" =sha256:e131100d1b0f8424d513f2f299f7d58bd6fdc8f5db8b0a87d5cfa45e45a58254
  note: re-read after the commit that fixes what the pre-merge gate found. The section now also collects the numbers the branch repeats by itself. Which side moves is untouched: the receiving commit's numbers are still taken as fixed and only ids the branch introduces are ever mapped.
- 2026-09-14T21:05:00-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/renumber.py § "plan" =sha256:e131100d1b0f8424d513f2f299f7d58bd6fdc8f5db8b0a87d5cfa45e45a58254
  artifact: sha256:6441d5a08eff4d46321df05ea98f1c6758ffb830f2bb2919338b9fc80a4bc7cc
  note: propagated from a moved ground

- 2026-09-14T21:05:02-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/renumber.py § "plan" =sha256:6441d5a08eff4d46321df05ea98f1c6758ffb830f2bb2919338b9fc80a4bc7cc
  note: re-read after the commit that answers the gate's second round. Which side moves is untouched: the receiving commit's numbers are still taken as fixed and only ids the branch introduces are mapped. What the section gained is the order it asks git in, and the set of numbers entries still answer to.

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
- docs/OPERATING.md · standing · cites-as-live
