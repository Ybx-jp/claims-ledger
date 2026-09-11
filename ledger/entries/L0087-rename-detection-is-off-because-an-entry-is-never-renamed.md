---
id: L0087-rename-detection-is-off-because-an-entry-is-never-renamed
kind: claim
stated: 2026-09-08T02:30:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 65e0241cd2a42b9683d29244f895a0fe734c88914fa3666ade200cd7d480cd78
---

## Assertion

The history walk runs without rename detection, because an entry is never renamed: its id is its filename.

## Scope

metric: whether the walk asks git to follow renames
cohort: the history walk under the entries directory
condition: a successor is often written as a near-copy of its predecessor

## Grounds

- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

git_history is called without --follow. Rename detection compares each file against every file in the parent commit, so a successor written as a near-copy of a predecessor still in the tree is reported as renamed from it, and the creating commit comes back as one where this file did not exist — leaving the frozen-region comparison reading the wrong blob entirely. An entry's filename is its id and does not change, so there is nothing here for the detection to find and everything for it to invent.

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
  note: read against the working tree after the only edit to check_history since the reading at 2a76453, a comment naming the audit file by its path docs/audits/ARCH-AUDIT.md instead of by its bare name: git_history is still called without --follow; the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
