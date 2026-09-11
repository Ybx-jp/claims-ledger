---
id: L0140-a-version-control-commands-exit-status-is-kept
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: b28d18d071dd47be7b85142a8077d02825f38864bf18e077b06030460c413a36
---

## Assertion

A version-control command's exit status is carried back alongside its output, so a command that could not answer is never read as a benign negative.

## Scope

metric: whether a failed command and a command answering no are distinguishable to a caller
cohort: every version-control call in the package
condition: both produce empty output

## Grounds

- code: src/claims_ledger/schema.py § "GitAnswer" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "git_call" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

git_call returns the exit code, the output and a reason as one value, and each caller then says for itself which non-zero exits are answers — a revision that is simply absent — and which are the command failing to answer at all. The convenience wrapper that folds both into nothing is kept for the callers to whom they really are the same thing. A caller reading that fold as a negative turns a broken repository into a report that a check passed, which is the one output this package must never produce.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "GitAnswer" @4af0acd253eeef1571cd7615ea3a041eda9e945e
  artifact: 36052faf227379aac7e17f339c1c6b3937d1f6c1
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "GitAnswer" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed
- 2026-09-11T03:09:46-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "GitAnswer" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  artifact: sha256:a7440329bcef4608350e605e347143074db7422b4becaf4972ac3478137e7620
  note: propagated from a moved ground
- 2026-09-11T03:09:46-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "GitAnswer" =sha256:a7440329bcef4608350e605e347143074db7422b4becaf4972ac3478137e7620
  note: read against the working tree after one comment in the section began naming the audit file by its docs/audits path, since the reading at 2a76453: the dataclass, its fields and the exit status carried beside the output are unchanged; the assertion holds as written.

## References

- src/claims_ledger/schema.py · standing · cites-as-live
