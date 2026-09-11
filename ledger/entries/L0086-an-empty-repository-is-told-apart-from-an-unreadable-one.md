---
id: L0086-an-empty-repository-is-told-apart-from-an-unreadable-one
kind: claim
stated: 2026-09-08T02:30:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: be94edc73ea4f6b0b33d681ac32e8123be46c563da4795d354abf4443fce908d
---

## Assertion

A repository holding no commits is told apart from one that cannot be read: the empty repository is an ordinary state, and the unreadable one is a failure.

## Scope

metric: whether an empty repository and an unreadable one produce the same outcome
cohort: ledgers under a repository
condition: git log exits non-zero for both

## Grounds

- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_history asks rev-parse --verify --quiet HEAD before the walk and uses that answer to decide what an empty revision list means. Both conditions produce the same empty list out of git log, so collapsing them would either report a ledger being scaffolded as broken or pass a repository nothing could read. The question is asked once, at the top, rather than inferred from the walk's silence.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d
  artifact: 3ebabaa4d367b5f9fa08dd065da0555734c20f01
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_history" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed
- 2026-09-11T03:10:33-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_history" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  artifact: sha256:a0f5460dc7e6805f42f37f08c07a994eaac5dd9d160914c883daecf28f17db9b
  note: propagated from a moved ground
- 2026-09-11T03:10:33-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_history" =sha256:a0f5460dc7e6805f42f37f08c07a994eaac5dd9d160914c883daecf28f17db9b
  note: read against the working tree after the only edit to check_history since the reading at 2a76453, a comment naming the audit file by its path docs/audits/ARCH-AUDIT.md instead of by its bare name: rev-parse --verify --quiet HEAD is still asked once before the walk and its answer still decides what an empty revision list means; the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
