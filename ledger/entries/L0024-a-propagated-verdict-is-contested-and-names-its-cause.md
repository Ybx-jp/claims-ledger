---
id: L0024-a-propagated-verdict-is-contested-and-names-its-cause
kind: claim
stated: 2026-09-07T23:17:47-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 83f2c24eb4c004315a9ad16f2ac486a066d429f89eca091d8b39442e67954fe5
---

## Assertion

Every verdict the propagation machinery composes is contested, attributed to the configured propagation author, and carries its cause as an `entry:` pointer with the act that caused it.

## Scope

metric: the status, author and evidence pointer of a composed propagated verdict
cohort: every verdict block propagate or freshness queues for append
condition: any cause, any act

## Grounds

- code: src/claims_ledger/propagate.py § "verdict_block" @0af113005f955a4e120d71338993a94cc6efeb7b

## Warrant

verdict_block returns a fixed three-line block: a status line whose status is the literal contested, carrying the grade and the author it was given; an evidence line whose pointer is `entry: <cause> · <act>`; and a note. There is no route through it to a propagated verdict of another status, or to one that names no cause.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
