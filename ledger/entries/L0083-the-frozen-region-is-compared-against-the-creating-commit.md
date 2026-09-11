---
id: L0083-the-frozen-region-is-compared-against-the-creating-commit
kind: claim
stated: 2026-09-08T02:30:45-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 183b56f4ed3cd68c891c93dabb12584d984495b9e1b7f89001f191a313c246cf
---

## Assertion

An entry's frozen region is compared against the blob at the commit that created the file, and not against its most recent revision.

## Scope

metric: which revision the frozen region is held to
cohort: committed entries
condition: an entry may have many revisions, all of them appends

## Grounds

- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_history takes the oldest revision the walk found for the path and reads the blob there. Comparing against the previous revision instead would make an edit to the frozen region permanent the moment it survived one commit. Comparing against the creating commit holds the region to what it was when the entry entered history, which is what the immutability the ledger promises actually says.

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
  note: read against the working tree after the only edit to check_history since the reading at 2a76453, a comment naming the audit file by its path docs/audits/ARCH-AUDIT.md instead of by its bare name: the frozen region is still read from the blob at the oldest revision the walk found for the path; the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
