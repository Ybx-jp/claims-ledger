---
id: L0158-a-distinction-is-legal-against-any-status
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6298ebe2622ba1eb8efe7ea8f741f19a7b9fe9f64108f387db4ceebdbdba6a0e
---

## Assertion

A distinguishes act is legal against a target of every status the schema has, so no verdict on the target can make the act illegal.

## Scope

metric: the target statuses each act is legal against
cohort: the distinguishes act
condition: every status the schema declares

## Grounds

- code: src/claims_ledger/schema.py § "ACT_ALLOWS" @aadceb0aba82a85fe71b15394896c43977751709
- code: src/claims_ledger/references.py § "run" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

ACT_ALLOWS maps distinguishes to the whole status vocabulary, and references reads that map rather than a rule of its own, so there is one table to change and no second opinion. The reason is not the one cites-as-fallen has: a distinction is a claim about two Scopes rather than about a truth, and a target that is refuted, superseded or non-comparable was still a different claim about the same artifact. Grounds are frozen once committed, so an act that could be made illegal by somebody else's verdict would be a failure with no repair.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:17:13-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "ACT_ALLOWS" @aadceb0aba82a85fe71b15394896c43977751709
  artifact: c5b5dfd25c552c75745d3195f6b7e593a401b19e
  note: propagated from a moved ground

- 2026-09-08T14:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "ACT_ALLOWS" @ee234ed85969dcc0c8400721f9a16162d6cee9f5
  note: read against commit ee234ed: the citing comment moved into this section from outside it, so the section now carries the sentence it always managed, into the literal; every act still maps to the same statuses and distinguishes still takes all of them
- 2026-09-08T14:43:44-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/references.py § "run" @aadceb0aba82a85fe71b15394896c43977751709
  artifact: f9db731e0b23468e3e0628c6ac6c35712cd7310d
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/references.py § "run" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed
- 2026-09-11T03:10:06-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/references.py § "run" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  artifact: sha256:f70bdd5d1e540e25c19e6de691f1c670b4c121ef585d25c54b0f8304ce9dba26
  note: propagated from a moved ground
- 2026-09-11T03:10:06-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/references.py § "run" =sha256:f70bdd5d1e540e25c19e6de691f1c670b4c121ef585d25c54b0f8304ce9dba26
  note: read against the working tree after run gained a `minted` set and a skip for citation-shaped parentheticals whose id this ledger never minted, the placement check appended after the roster check, and one renumbered citation, since the reading at 2a76453: references still reads ACT_ALLOWS for every act and keeps no rule of its own for distinguishes, and the added unminted-id skip touches only document parentheticals whose act is not a citation act; the assertion holds as written.

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- docs/SCHEMA.md · standing · cites-as-live
- README.md · standing · cites-as-live
