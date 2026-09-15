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

- 2026-09-14T20:21:10-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/renumber.py § "reanchor" =sha256:b018c29135af102ccee1e40faea80ea9ca37c20feece45565a5a2a9ac94c2c9b
  artifact: sha256:bf8aa11df4c61b1041f6e3d50277ee2fc5b0e1b60204ba5eae8e5349d843271d
  note: propagated from a moved ground

- 2026-09-14T20:21:11-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/renumber.py § "reanchor" =sha256:bf8aa11df4c61b1041f6e3d50277ee2fc5b0e1b60204ba5eae8e5349d843271d
  note: re-read after the commit that fixes what the pre-merge gate found. The proof is unchanged and now runs over the verdicts' evidence as well as the Grounds, and its answer is recorded so that every commit of one rewrite gets the same one. What this claim asserts — that an anchor moves only where undoing the substitution reproduces the anchor already written — is what the recorded decision records.
- 2026-09-14T21:05:00-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/renumber.py § "reanchor" =sha256:bf8aa11df4c61b1041f6e3d50277ee2fc5b0e1b60204ba5eae8e5349d843271d
  artifact: sha256:1f9e313b6e2ceb128de300dabbcb01f54ded0ae5ed4d01bd7610230dd1fcd321
  note: propagated from a moved ground

- 2026-09-14T21:05:02-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/renumber.py § "reanchor" =sha256:c40357926e15956d99757a22b89aeca18a1b2a5cde911552cd1f9473bf25767b
  note: re-read after the commit that answers the gate's second round. The proof is unchanged — an anchor moves only where undoing the substitution reproduces the anchor already written — and what moved around it is when the question is asked and where the answer is kept.

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
