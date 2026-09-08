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

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
