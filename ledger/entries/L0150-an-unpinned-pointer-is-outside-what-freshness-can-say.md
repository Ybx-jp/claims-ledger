---
id: L0150-an-unpinned-pointer-is-outside-what-freshness-can-say
kind: claim
stated: 2026-09-08T02:46:27-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: a1680cab981429a838aa6516ecd273ae0498d82b89b654c5c415882780212bf4
---

## Assertion

A pointer using an unpinned marker is only as reproducible as the working tree it names, and the freshness checker cannot speak to it.

## Scope

metric: what the freshness checker reports for a pointer with no revision in its pin
cohort: pointers using an unpinned marker
condition: a ledger outside version control, and the red-team corpus, need one

## Grounds

- code: src/claims_ledger/schema.py § "UNPINNED" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

UNPINNED names the markers that mean the artifact is read from the working tree as it stands. With no revision there is nothing to compare against, so the checker that exists to notice an artifact moving under a claim is silent by construction — not because the ground is fresh, but because freshness is undefined for it. A ledger kept outside version control needs the escape hatch and the corpus uses it; anywhere else it is a pointer whose evidence is whatever happened to be on disk.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "UNPINNED" @4af0acd253eeef1571cd7615ea3a041eda9e945e
  artifact: 36052faf227379aac7e17f339c1c6b3937d1f6c1
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "UNPINNED" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

## References

- src/claims_ledger/schema.py · standing · cites-as-live
