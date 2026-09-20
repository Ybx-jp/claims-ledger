---
id: L0199-an-anchor-at-a-commit-is-the-digest-of-the-section-there
kind: claim
stated: 2026-09-10T22:03:58-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 355ca6ffa16ed3fa445f4eef4971375d3980336f69b762fceadcf5fd76ff0377
---

## Assertion

An anchor stated at a commit names the digest of the named section as that commit has it, computed with the same function a by-value anchor is, so both forms of anchor name the same kind of datum and one comparison serves both.

## Scope

metric: what an anchor written as a commit is reduced to before comparison
cohort: every checked evidence pointer anchored at a commit, in Grounds and in readings
condition: version control can show the path at that commit

## Grounds

- code: src/claims_ledger/freshness.py § "anchor_digest" =sha256:092387637d51b82ca6a044fd946f230a7b9f0fe3efe86e32a8d44cceaf0f3093

## Warrant

anchor_digest returns the pointer's own digest for an anchor stated by value, and for one stated at a commit reads the path at that commit, finds the section through the configured pattern and hands it to digest_of, the function section_digest uses; the answer is kept per pointer for the run. A section absent at the commit yields nothing to compare, which resolve reports, and a show that fails is reported as a question git declined. Reducing both forms to one digest is what lets the rest of the checker, the discharge and the orphan rule included, treat a ground and a reading alike whichever way each was written.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-20T12:09:31-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "anchor_digest" =sha256:092387637d51b82ca6a044fd946f230a7b9f0fe3efe86e32a8d44cceaf0f3093
  artifact: sha256:48618c3d60bc94838fa0ae169e665adfcce74e496314214b6ba47bee341626ae
  note: propagated from a moved ground

- 2026-09-20T12:09:32-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "anchor_digest" =sha256:48618c3d60bc94838fa0ae169e665adfcce74e496314214b6ba47bee341626ae
  note: this repository adopted the decorator-aware `code` pattern it documents, so the section no longer runs on to the decorator of the definition below it; anchor_digest itself is unchanged

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
