---
id: L0046-an-uncited-verbatim-assertion-is-a-failure
kind: claim
stated: 2026-09-08T02:08:33-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: adf701e463dfe43c21e4fbef2dc7ba8a0ae140362851e32e6e0859d92f8f1d77
---

## Assertion

A document that carries an entry's Assertion verbatim, after normalization, fails unless it also cites that entry.

## Scope

metric: whether a document holding an entry's Assertion word for word is reported when it carries no citation of it
cohort: configured documents, and Assertions of at least twenty normalized characters
condition: the document is readable

## Grounds

- code: src/claims_ledger/references.py § "run" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487

## Warrant

run normalizes the document body once and each Assertion the same way, so whitespace and unicode differences cannot hide a copy, then reports a containment the document's own citations do not account for. The length floor keeps a short Assertion from matching incidental prose. What this catches is copies: a claim restated in other words falls outside it, and the check says nothing about one.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T09:41:22-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/references.py § "run" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487
  artifact: d6569fb97a267a37b74525a3f5ea5ca18695adc6
  note: propagated from a moved ground

- 2026-09-08T09:50:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/references.py § "run" @5ee55ae6992f10c834510759f026644f42614025
  note: read against the change in commit 5ee55ae, which narrowed the dependent exemption from FALLEN to TERMINAL in that one branch; this claim names a different part of the same section and is unaffected
- 2026-09-11T03:10:06-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/references.py § "run" @5ee55ae6992f10c834510759f026644f42614025
  artifact: sha256:f70bdd5d1e540e25c19e6de691f1c670b4c121ef585d25c54b0f8304ce9dba26
  note: propagated from a moved ground
- 2026-09-11T03:10:06-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/references.py § "run" =sha256:f70bdd5d1e540e25c19e6de691f1c670b4c121ef585d25c54b0f8304ce9dba26
  note: read against the working tree after run gained a docstring, a `minted` set and a skip for citation-shaped parentheticals whose id this ledger never minted, the placement check appended after the roster check, and one renumbered citation, since the reading at 5ee55ae: the normalized-body containment check of each Assertion, with its length floor and the exemption for a document that cites the entry, is unchanged; the assertion holds as written.

## References

- src/claims_ledger/references.py · standing · cites-as-live
