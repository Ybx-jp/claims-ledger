---
id: L0207-sha-write-fills-a-pending-anchor-from-the-tree
kind: claim
stated: 2026-09-11T02:55:50-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 3d8fd31b2d10373e4c4d92afae4b7fa632b7fca6a54b1ab03e51e9d709f22b03
---

## Assertion

sha --write fills every evidence pointer whose anchor is the placeholder, in the Grounds and in verdict evidence alike, with the digest of its section as the working tree has it, refuses by name a pointer whose text the tree does not hold before writing anything, and refuses to fill one in the Grounds of a committed entry unless --force is passed.

## Scope

metric: what sha --write does with an evidence pointer whose anchor is the placeholder
cohort: every evidence pointer of the entry being written, in its Grounds and in each verdict's evidence
condition: --write is passed; without it the placeholders are left as written and reported by validate

## Grounds

- code: src/claims_ledger/authoring.py § "anchors_to_fill" =sha256:07fc8708a22ce06e398a0b1b959a42a50cd1444c20992498b960c16c34b07b04
- code: src/claims_ledger/authoring.py § "restamp" =sha256:462643362dd16beb66b7c055e703fda5f8d8a7cf2d2722a33eb4c2f2789f9c23

## Warrant

anchors_to_fill walks the Grounds and every verdict's evidence, and for each evidence pointer whose anchor is the placeholder reads the path from the working tree and digests the named section, or the whole text for a plain pointer, through the same functions the freshness comparison uses; a path that is not a file, one that cannot be read, or a section not in it raises before restamp writes, so a fingerprint is never written beside an anchor that could not be. restamp asks git whether the entry is committed only when the write would touch the frozen region, which a new fingerprint and a Grounds anchor do and a verdict's evidence, below the APPEND marker, does not; then it fills every occurrence of each pending pointer at line end and writes once, atomically.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/authoring.py · standing · cites-as-live
