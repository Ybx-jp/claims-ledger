---
id: L0278-a-marker-is-declared-where-a-checker-reads-it
kind: claim
stated: 2026-09-20T10:22:13-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6f04af8ca0cf62f03bf5db6a14975dcc7535821baf9e231b5c425d51d71603c3
---

## Assertion

A marker written into a configured document is declared in the entry's References, and one written anywhere else is not.

## Scope

metric: whether the lift writes a References row for the marker
cohort: the markers a lift writes
condition: the artifact the ground names is, or is not, selected by the document globs

## Grounds

- code: src/claims_ledger/lift.py § "reference_row" =sha256:bddce6415daf064cea43e8e0037b6f1018b24c8e346781be9f09cdf6f66c959a

## Warrant

A citation is a citation where a checker reads one. Where the artifact is a configured document, references reads the marker and fails until the entry lists the citing document, so a lift that wrote the marker alone would leave a failing check behind it. Where the artifact is not a document, the row is itself the failure, because references reports a row naming a file it cannot see. reference_row asks selects_document, which is the same membership test every other reader of the document globs asks, so the two cannot come to disagree about what a document is.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/lift.py · standing · cites-as-live
- README.md · standing · cites-as-live
