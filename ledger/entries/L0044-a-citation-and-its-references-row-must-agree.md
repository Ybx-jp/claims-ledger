---
id: L0044-a-citation-and-its-references-row-must-agree
kind: claim
stated: 2026-09-08T02:08:33-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: aa50d521109f632c90ee37209174147d03c9e5bdb225bbea406ee2de52b84fe9
---

## Assertion

A document citing an entry fails unless that entry's References section lists the document with the same act, and a References row fails unless the document it names really cites the entry that way.

## Scope

metric: whether each side of the document-to-entry correspondence is checked against the other
cohort: inline citations in configured documents, and References rows in entries
condition: the document is readable and among the configured documents

## Grounds

- code: src/claims_ledger/references.py § "run" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487

## Warrant

run builds, per document, the set of id-and-act pairs it actually found, and checks the correspondence twice against that same set: a citation whose target lists no matching row fails as the citation is read, and afterwards every References row is looked up in the set recorded for the document it names. A row naming a document the checker cannot see is reported as that rather than as a mismatch, so a configuration gap and a wrong act are told apart in the report.

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
  note: read against the working tree after run gained a docstring, a `minted` set and a skip for citation-shaped parentheticals whose id this ledger never minted, the placement check appended after the roster check, and one renumbered citation, since the reading at 5ee55ae: the per-document set of id-and-act pairs, the failure for a citation with no matching References row, and the later pass over every References row against that set are unchanged; the assertion holds as written.

## References

- src/claims_ledger/references.py · standing · cites-as-live
