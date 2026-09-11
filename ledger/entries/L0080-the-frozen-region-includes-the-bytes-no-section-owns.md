---
id: L0080-the-frozen-region-includes-the-bytes-no-section-owns
kind: claim
stated: 2026-09-08T02:30:44-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 3566fe314b5aa9afa28ea8dfce50522a81ec967f8f19c4e24b065ce83f48b481
---

## Assertion

The frozen region is compared in full, including the bytes above the opening heading that belong to none of the sections a report can name.

## Scope

metric: whether a change above the opening heading is caught
cohort: the region above the APPEND marker
condition: a section runs from its own heading to the next

## Grounds

- code: src/claims_ledger/validate.py § "_frozen_region" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

A section runs from its own heading to the next, so every byte before the opening heading belongs to none of them and the section-by-section comparison cannot see it. _frozen_region takes the whole span above the marker, and check_history compares it as one string and reports it under its own name. The scaffold leaves that span empty, which is exactly what made it a hiding place: nothing legitimate is written there, so nothing legitimate ever changes there.

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
  note: read against the working tree after the only edit to check_history since the reading at 2a76453, a comment naming the audit file by its path docs/audits/ARCH-AUDIT.md instead of by its bare name: the whole span above the marker is still taken by _frozen_region and compared as one string under its own name; the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
