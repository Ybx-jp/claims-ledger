---
id: L0039-a-consultation-sentence-naming-another-author-is-flagged
kind: claim
stated: 2026-09-08T02:02:28-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 2b6988046b299d7d539a080188c495e2a407ddf19b19658e388a618cd9612000
---

## Assertion

A verified consultation quote whose source sentence names an author registered on a different source, or the phrase et al., is flagged as material the expert may be relaying.

## Scope

metric: whether a flag is raised for a verified consultation span whose source sentence names another registered author
cohort: Backing blocks on consultation-type sources that verify
condition: the block is being checked in its own right, rather than to reproduce a retraction's defect

## Grounds

- code: src/claims_ledger/resolve.py § "check_quote" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
- code: src/claims_ledger/resolve.py § "sentence_bounds" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
- code: src/claims_ledger/resolve.py § "Sources" @ec82c16045421ce5a6cb71befe8ddbe6067489ae

## Warrant

With the spans located and the block otherwise clean, check_quote widens each span to the sentence containing it using sentence_bounds, then searches that sentence for the surnames Sources.surnames_elsewhere gathers from every other registry row, and for et al. A hit is a flag rather than a failure, because the sentence may still be the expert's own judgment; what the flag settles is that a reader is told where relayed authority may be standing in for a primary source.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
