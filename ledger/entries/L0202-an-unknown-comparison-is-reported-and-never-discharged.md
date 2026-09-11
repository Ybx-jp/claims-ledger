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

## References
- src/claims_ledger/freshness.py · standing · cites-as-live
