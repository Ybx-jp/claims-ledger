---
id: L0307-an-anchor-is-re-pinned-to-the-rewritten-text-it-names
kind: claim
stated: 2026-09-24T22:15:42-07:00
author: main
grade: measured
supersedes: L0238-an-anchor-is-re-pinned-only-where-the-id-is-proved-to-be-the-whole-change
verbatim_change: the Assertion and the Scope condition now take the re-pin from the version of the artifact that holds the named text rather than from the tip alone, so a drifted anchor names the rewritten text instead of text no commit holds; Backing is unchanged and there is none
verbatim_sha: f3c7e96bdc5805d2052f11b379166ace9fdb453d46b1bbbbc7c1c1d0112a52c3
---

## Assertion

A by-value anchor is re-pinned by a renumber only to the rewritten version of the text it names: a version of the artifact the branch holds whose section digests to the anchor, with the substitution applied. Any other change in the span since is left for freshness to report.

## Scope

metric: the anchors a renumber rewrites
cohort: every by-value anchor of every rewritten entry
condition: the anchor names a sectioned artifact, and some commit of the rewritten branch holds the text it names

## Grounds

- code: src/claims_ledger/renumber.py § "reanchor" =sha256:3adae19f29d4e27988e3cd66e9497330666a79ba6307047438054e81ea9e27f5

## Warrant

reanchor walks the versions decide_anchors supplies, takes the first whose section digests to the anchor already written, and re-pins to the digest of that same section as the rewritten commit will hold it; the two texts differ only by the substitution, so the re-pin is a proof that the id is the whole of the change between them rather than a re-pin on trust. It never digests the tip unless the tip holds the named text, so a span that drifted after the reading still differs from the new anchor, and freshness flags it as before.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
- docs/OPERATING.md · standing · cites-as-live
