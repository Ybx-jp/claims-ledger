---
id: L0019-a-challenges-act-against-a-terminal-target-appends-nothing
kind: claim
stated: 2026-09-07T23:17:46-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 081fe534b84a8a9729f6fd09a27ec8055feea37ecbabbcd93e4a8c973156e34e
---

## Assertion

A `challenges` act whose target has reached a terminal status is reported as illegal and nothing is appended to that target.

## Scope

metric: the reports propagate returns, and whether a verdict is queued, for a challenges act against a terminal target
cohort: challenges acts whose target's derived status is terminal
condition: a propagate run with or without --write

## Grounds

- code: src/claims_ledger/propagate.py § "run" @0af113005f955a4e120d71338993a94cc6efeb7b

## Warrant

the challenges branch tests the target's status against TERMINAL before anything else and, when it matches, appends only a fail Report saying the act is illegal and that a fallen entry is cited cites-as-fallen; the queueing of a verdict sits in the elif that this branch has already taken, so it is never reached.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T09:41:22-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/propagate.py § "run" @0af113005f955a4e120d71338993a94cc6efeb7b
  artifact: d7edcf2d43d01f126a1240c49607dcd4d379e414
  note: propagated from a moved ground

- 2026-09-08T09:50:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" @5ee55ae6992f10c834510759f026644f42614025
  note: read against the change in commit 5ee55ae, which narrowed the dependent exemption from FALLEN to TERMINAL in that one branch; this claim names a different part of the same section and is unaffected

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
