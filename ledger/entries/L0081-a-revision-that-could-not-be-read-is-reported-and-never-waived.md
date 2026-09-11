---
id: L0081-a-revision-that-could-not-be-read-is-reported-and-never-waived
kind: claim
stated: 2026-09-08T02:30:44-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 423e9a1ec5d4f59bef03a518ce350562bbd2de95ac0993fc8f1ca95f97f2f2aa
---

## Assertion

A revision the append-only check could not read is reported as unchecked, rather than passed over as one across which nothing changed.

## Scope

metric: the outcome for a revision whose blob could not be read
cohort: revisions of an entry, their parents, and HEAD
condition: a parent git reports as missing is the revision the entry was created on

## Grounds

- code: src/claims_ledger/validate.py § "_unread_verdicts" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_history routes every unreadable blob through _unread_verdicts, which names the revision, the path and git's reason, and says that across that revision it was not checked that verdicts only appended. The single exception is a parent git calls missing, which is the edge the entry was created on and has nothing on its far side to compare. Waiving the rest would turn a git that could not answer into a clean run over history nobody read.

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
  note: read against the working tree after the only edit to check_history since the reading at 2a76453, a comment naming the audit file by its path docs/audits/ARCH-AUDIT.md instead of by its bare name: every unreadable blob is still routed through _unread_verdicts with the revision, path and reason named, and only a missing parent is passed over; the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
