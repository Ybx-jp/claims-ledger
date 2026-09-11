---
id: L0047-an-unreadable-document-is-a-failure-not-a-clean-run
kind: claim
stated: 2026-09-08T02:08:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0de37bc16bdd8be501e2e7b73c455ed98a270f634191361261f00f9ca9e58ccf
---

## Assertion

A configured document the checker could not open or decode is reported as a failure, so a run that read fewer documents than the configuration names cannot exit clean.

## Scope

metric: the outcome for a configured document that could not be read
cohort: documents named by the configuration, whether they fail at discovery or at the read
condition: the rest of the ledger checks clean

## Grounds

- code: src/claims_ledger/references.py § "run" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487

## Warrant

run reports both populations: the documents discovery could not open, which the ledger carries alongside the ones it could, and the ones that fail at the read here. Each is a failure rather than a flag, because the exit code is what a hook acts on, and a document whose citations were never read is a document over which nothing was verified.

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
  note: read against the working tree after run gained a docstring, a `minted` set and a skip for citation-shaped parentheticals whose id this ledger never minted, the placement check appended after the roster check, and one renumbered citation, since the reading at 5ee55ae: the failures for a document discovery could not open and for one whose read fails here are unchanged, and the added placement pass reads no document of its own; the assertion holds as written.

## References

- src/claims_ledger/references.py · standing · cites-as-live
