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

- 2026-09-11T19:50:54-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "Sources" =sha256:10b6e2e89ca3151df0f26d542563a1e0be7f6c72ddf21c655f1c4187173c549a
  note: re-read after the commit that has this reader take the source registry from the index when the run was asked for the index. Which registry is read is a new question here; what a row says, and what a missing row does, are unchanged.

- 2026-09-11T22:04:31-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "Sources" =sha256:96e0d8199e6c027a3f2c3838f40301b237366c23c0be0d137303dd06c41e583a
  note: re-read after the commit answering the fix-review gate on this branch (qe ticket e9b7d35601214a1b). A registry git could not hand over now stops the run rather than falling back to the working tree's. Which registry is read under the flag is unchanged.

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
