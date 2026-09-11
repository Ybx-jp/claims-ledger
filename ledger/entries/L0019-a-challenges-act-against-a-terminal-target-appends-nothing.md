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
- 2026-09-11T03:09:46-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/propagate.py § "run" @5ee55ae6992f10c834510759f026644f42614025
  artifact: sha256:0ca4d23c82c30d940fab79c0e6c5feb672853f2c9f34db3401c9efbd0d9f8e59
  note: propagated from a moved ground
- 2026-09-11T03:09:46-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" =sha256:0ca4d23c82c30d940fab79c0e6c5feb672853f2c9f34db3401c9efbd0d9f8e59
  note: read against the working tree after run gained a docstring carrying the citations for the rules it holds, moved into the span the grounds pin, since the reading at 5ee55ae: the code of the section is byte-identical once the docstring is set aside, so a challenges act against a terminal target is still reported as illegal with nothing appended; the assertion holds as written.

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
