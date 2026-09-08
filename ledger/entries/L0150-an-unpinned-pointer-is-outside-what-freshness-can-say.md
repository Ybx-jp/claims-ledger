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

## References

- src/claims_ledger/schema.py · standing · cites-as-live
