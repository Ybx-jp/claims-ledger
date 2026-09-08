---
id: L0021-without-write-nothing-is-modified
kind: claim
stated: 2026-09-07T23:17:46-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 62a53c7900b077b1f95cdcb4c40a274c6f6eb5f3a3e26ae5ab01d1c53b971c6d
---

## Assertion

A propagate run without `--write` leaves every file as it found it: the verdicts it finds missing are reported and queued, and the queue is discarded when the run returns.

## Scope

metric: whether any file is modified by a propagate run
cohort: propagate runs over a ledger owing one or more propagated verdicts
condition: --write absent

## Grounds

- code: src/claims_ledger/propagate.py § "run" @0af113005f955a4e120d71338993a94cc6efeb7b

## Warrant

run collects every verdict it would append into a list local to the call, and the only call that touches a file sits inside the `if write:` branch; with write false that branch is skipped and the list goes out of scope with the function, so the reports are the whole of what the run produces.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
