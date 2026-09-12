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
  note: read against the working tree after run gained a docstring carrying the citations for the rules it holds, moved into the span the grounds pin, since the reading at 5ee55ae: the code of the section is byte-identical once the docstring is set aside, so without --write the queue of missing verdicts is still reported and discarded and no file is written; the assertion holds as written.

- 2026-09-11T19:41:48-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" =sha256:8fa19789e9badc1682afa37198032a2207b9e89ef81a5b34d8ec9cfeccb3aa67
  note: re-read after the same commit, which gives this checker a cached mode: it takes the flag and passes it to the entry load. The walk and every rule in it are unchanged.

- 2026-09-11T22:04:31-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" =sha256:41d276552f5f6f4ff4d4c194a4fcb58c2ca9d002bffa7d081767f36be10289ea
  note: re-read after the commit answering the fix-review gate on this branch (qe ticket e9b7d35601214a1b). This checker now takes its entries through `entries_for`, so a run that will append decides from the tree it appends to. Every rule this claim is about is untouched; what moved is which tree the list came from when `--write` is on.

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
