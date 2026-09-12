---
id: L0026-a-propagated-fall-carries-the-grade-of-the-fall
kind: claim
stated: 2026-09-07T23:17:47-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: e10fdd91c2889d3f9333e380e7c359ee000f7f0621ddabdfc9191d4a9d8b7644
---

## Assertion

A verdict propagated from a fall takes its grade from the target's own falling verdict, and its note names that verdict's index and timestamp, so the flag says which fall caused it.

## Scope

metric: the grade and note of a propagated contested verdict
cohort: verdicts propagated from a live-cited ground that fell
condition: the target carries a verdict whose status is fallen, or carries none that can be found

## Grounds

- code: src/claims_ledger/propagate.py § "falling_verdict" @0af113005f955a4e120d71338993a94cc6efeb7b
- code: src/claims_ledger/propagate.py § "run" @0af113005f955a4e120d71338993a94cc6efeb7b

## Warrant

falling_verdict returns the target's earliest verdict whose status is in FALLEN, and run hands that verdict's grade to verdict_block and writes its index and timestamp into the note; the target's own grade and a literal unknown are used only when no such verdict is there to read.

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
  note: read against the working tree after run gained a docstring carrying the citations for the rules it holds, moved into the span the grounds pin, since the reading at 5ee55ae: the code of the section is byte-identical once the docstring is set aside, so a verdict propagated from a fall still takes its grade from the falling verdict and names that verdict's index and timestamp in its note; the assertion holds as written.

- 2026-09-11T19:41:48-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" =sha256:8fa19789e9badc1682afa37198032a2207b9e89ef81a5b34d8ec9cfeccb3aa67
  note: re-read after the same commit, which gives this checker a cached mode: it takes the flag and passes it to the entry load. The walk and every rule in it are unchanged.

- 2026-09-11T22:04:31-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" =sha256:41d276552f5f6f4ff4d4c194a4fcb58c2ca9d002bffa7d081767f36be10289ea
  note: re-read after the commit answering the fix-review gate on this branch (qe ticket e9b7d35601214a1b). This checker now takes its entries through `entries_for`, so a run that will append decides from the tree it appends to. Every rule this claim is about is untouched; what moved is which tree the list came from when `--write` is on.

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
