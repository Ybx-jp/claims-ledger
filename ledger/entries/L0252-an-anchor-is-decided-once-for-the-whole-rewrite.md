---
id: L0252-an-anchor-is-decided-once-for-the-whole-rewrite
kind: claim
stated: 2026-09-14T20:20:01-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6aac83f8efe9477875542cd5670971b1f8a90d7a0327a898b94514acda446689
---

## Assertion

A renumber decides each anchor once, where the entry it belongs to is created, and writes that same answer into every later commit of the rewrite.

## Scope

metric: the anchor a rewritten entry carries across the commits of one rewrite
cohort: every by-value anchor a rewrite re-pins
condition: the entry appears in more than one commit of the branch

## Grounds

- code: src/claims_ledger/renumber.py § "reanchor" =sha256:bf8aa11df4c61b1041f6e3d50277ee2fc5b0e1b60204ba5eae8e5349d843271d

## Warrant

reanchor records each decision under the entry's id and the pointer as written and applies the recorded answer thereafter; a span can be one thing where the entry is created and another two commits later, so deciding per commit writes one frozen region at the creating commit and a different one after it, which is what validate refuses.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
