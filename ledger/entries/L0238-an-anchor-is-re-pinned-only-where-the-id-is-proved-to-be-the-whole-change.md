---
id: L0238-an-anchor-is-re-pinned-only-where-the-id-is-proved-to-be-the-whole-change
kind: claim
stated: 2026-09-14T19:13:42-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9de822306494414c8e4770d274aec5a79a7dfaa2b31407851a80c5a1a71d9dd8
---

## Assertion

A by-value anchor is re-pinned by a renumber only when undoing the substitution reproduces the anchor the entry already carries; any other change in the span leaves the anchor as written.

## Scope

metric: the anchors a renumber rewrites
cohort: every by-value ground of every rewritten entry
condition: the ground names a sectioned artifact the rewrite also holds

## Grounds

- code: src/claims_ledger/renumber.py § "reanchor" =sha256:b018c29135af102ccee1e40faea80ea9ca37c20feece45565a5a2a9ac94c2c9b

## Warrant

reanchor recomputes the digest of the section with the substitution undone and rewrites the anchor only when that equals the anchor already written, so the re-pin is a proof that the id was the whole of the change rather than a re-pin on trust; where it is not, the anchor stands and freshness flags it for a person to read.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
