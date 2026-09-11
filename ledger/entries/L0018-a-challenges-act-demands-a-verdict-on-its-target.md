---
id: L0018-a-challenges-act-demands-a-verdict-on-its-target
kind: claim
stated: 2026-09-07T23:17:46-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: a0e123746ff7740c990c940946fd4990935b38ccacd9e4650fe215b10a983044
---

## Assertion

An entry named by a `challenges` act must carry a contested verdict by the propagation author naming the challenger, and propagate reports the challenged entry — not the challenger — while it does not.

## Scope

metric: the reports propagate returns for the target of a challenges act, and which entry they are filed against
cohort: entries named by an `entry:` ground carrying the challenges act
condition: the challenged entry's status is not terminal

## Grounds

- code: src/claims_ledger/propagate.py § "run" @0af113005f955a4e120d71338993a94cc6efeb7b

## Warrant

the challenges branch of run's first pass asks has_propagated of the target rather than of the challenger, and both the Report it appends and the pending block it queues carry the target's prefix and path, so the flag lands on the entry that owes the verdict.

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
  note: read against the working tree after run gained a docstring carrying the citations for the rules it holds, moved into the span the grounds pin, since the reading at 5ee55ae: the code of the section is byte-identical once the docstring is set aside, so the challenged entry, not the challenger, is still the one reported while it lacks the verdict naming the challenger; the assertion holds as written.

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
