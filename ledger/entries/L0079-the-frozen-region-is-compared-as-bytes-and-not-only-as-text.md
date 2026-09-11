---
id: L0079-the-frozen-region-is-compared-as-bytes-and-not-only-as-text
kind: claim
stated: 2026-09-08T02:30:44-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9a838d40dcfa89ba614d412e6825493b4bbbf3f1ad5b24976b7e188301010f43
---

## Assertion

The frozen region is compared as bytes as well as text, so a region rewritten from CRLF to LF fails even though it reads the same.

## Scope

metric: whether a line-ending rewrite of the frozen region is caught
cohort: committed entries under a repository
condition: every other comparison decodes both sides through universal newlines

## Grounds

- code: src/claims_ledger/validate.py § "_frozen_bytes" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

_frozen_bytes takes the region out of the raw blob and out of the file's raw bytes, and check_history compares those two when the text comparisons have found nothing. Every other comparison in the checker decodes both sides, which folds CRLF and LF onto each other: an entry whose frozen region was rewritten line for line matched itself as text while every byte of it had changed. Immutable is a statement about bytes, so the bytes are what settles it.

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
  note: read against the working tree after the only edit to check_history since the reading at 2a76453, a comment naming the audit file by its path docs/audits/ARCH-AUDIT.md instead of by its bare name: the byte comparison of the frozen region through _frozen_bytes, made after the text comparisons find nothing, is unchanged; the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
