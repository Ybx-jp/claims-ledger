---
id: L0202-an-unknown-comparison-is-reported-and-never-discharged
kind: claim
stated: 2026-09-10T22:03:59-07:00
author: main
grade: measured
supersedes: L0116-a-drift-whose-artifact-cannot-be-stated-is-not-discharged
verbatim_sha: 0ceaa63c11811b8aaa0e9623fb1507844e3c4559ff0cf6bfce3b1ae0cc8a526c
---

## Assertion

A comparison that could not read the artifact is reported as unknown, stays undischarged whatever verdict names it, and leaves the entry unwritten, so every drift a verdict records was established from the artifact this run read.

## Scope

metric: what a writing run does when the artifact could not be determined
cohort: drifted grounds under --write
condition: the recorded artifact is the whole of what the orphan rule later checks

## Grounds

- code: src/claims_ledger/freshness.py § "run" =sha256:e95965ef764409d49cfc0a68bcbf017e722714e5427d9bb10082f5f6110e1793

## Warrant

run reports an unknown finding as a failure and moves on before any acknowledgement is weighed or any verdict block is queued, so a verdict is only ever written for a moved or withdrawn ground, and drift computes those findings and the digest they record from one read. A verdict recording nothing is one nothing could ever check: the orphan rule holds a discharge to its recorded artifact, so writing one for a comparison that did not happen would put an unfalsifiable discharge into the ledger from the moment it was made.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-11T22:04:31-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" =sha256:5845bd95fa9dbd8dfddbd89e398428975cac3ba77376d3ff4263898772561d03
  note: re-read after the commit answering the fix-review gate on this branch (qe ticket e9b7d35601214a1b). The same: the entries come through `entries_for` now. The comparison, what it records and when it writes are unchanged.

- 2026-09-12T15:32:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" =sha256:9b25e634a8f1b63fa4fdcf8d7f11ce70d7110ce3e78cf93ad24d03ee23c3efa7
  note: acknowledged: the run threads the ledger into `drift` for the cached reads. This claim is untouched by that (L0232).
- 2026-09-20T17:44:02-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "run" =sha256:9b25e634a8f1b63fa4fdcf8d7f11ce70d7110ce3e78cf93ad24d03ee23c3efa7
  artifact: sha256:52b08359937b4d1b390b0c2a0f9b6861f9d188c23cd83fbc9b16ebbcdf6b8faf
  note: propagated from a moved ground

- 2026-09-20T17:45:59-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" =sha256:52b08359937b4d1b390b0c2a0f9b6861f9d188c23cd83fbc9b16ebbcdf6b8faf
  note: The `unknown` branch — reported, never discharged, nothing appended — is byte-identical. What moved is above it: the reach handed to `effective_pointer`, which decides where a ground is compared from and not whether a comparison could be made.

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
