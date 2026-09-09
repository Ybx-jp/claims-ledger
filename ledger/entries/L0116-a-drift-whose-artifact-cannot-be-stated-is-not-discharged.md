---
id: L0116-a-drift-whose-artifact-cannot-be-stated-is-not-discharged
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0ceaa63c11811b8aaa0e9623fb1507844e3c4559ff0cf6bfce3b1ae0cc8a526c
---

## Assertion

A drift whose artifact this run cannot state is reported rather than discharged, and nothing is appended for it.

## Scope

metric: what a writing run does when the artifact could not be determined
cohort: drifted grounds under --write
condition: the recorded artifact is the whole of what the orphan rule later checks

## Grounds

- code: src/claims_ledger/freshness.py § "run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

run asks what the artifact is before it weighs any acknowledgement, and when the answer cannot be had it reports that no verdict was appended and why. A verdict recording nothing is one nothing could ever check: the orphan rule holds a discharge to its recorded artifact, so writing one without it would put an unfalsifiable discharge into the ledger from the moment it was made. The ledger is left as it was, and the run says why.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
  artifact: 7bf8ce83b6bb554674722efe7e644aa962b022ef
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
