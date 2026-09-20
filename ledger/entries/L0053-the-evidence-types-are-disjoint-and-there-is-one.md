---
id: L0053-the-evidence-types-are-disjoint-and-there-is-one
kind: claim
stated: 2026-09-08T02:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: c5feda5bd35b0860130fa0bdec2ab67d52a8bb4e4315d30f7df671061d339564
---

## Assertion

The declared evidence types are held to being disjoint and to being at least one: a type declared both sectioned and plain is refused, and a configuration declaring none at all is refused.

## Scope

metric: the outcome of declaring an evidence type twice, and of declaring zero
cohort: the sectioned and plain evidence type lists
condition: a measured grade requires an evidence ground

## Grounds

- code: src/claims_ledger/config.py § "from_table" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

from_table intersects the two lists and raises on any type in both, then raises when their union is empty. A type in both lists has two answers to whether a pointer of that type carries a section, and the checkers would take whichever they asked for. An empty union is a project where a measured grade has nothing it could rest on, which is a configuration that silently forbids the grade the ledger is mostly written in.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:42-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" @72ad99b4a138640f009ee09b911c741f84776135
  artifact: ddafd109dfd34f6f75aed2b26773ec283ee64d71
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed
- 2026-09-11T03:10:01-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  artifact: sha256:68ac3fee3de92f6a488946f8b0d0e81b3ce87100281630f31c69300920ed40a3
  note: propagated from a moved ground
- 2026-09-11T03:10:01-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:68ac3fee3de92f6a488946f8b0d0e81b3ce87100281630f31c69300920ed40a3
  note: read against the working tree after from_table gained, since the reading at 2a76453, a check that `citation-placement` is one of its three outcomes and passes it into Config: the sectioned and plain lists are still intersected and their union still refused when empty, in the same place; the assertion holds as written.
- 2026-09-14T19:21:53-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:68ac3fee3de92f6a488946f8b0d0e81b3ce87100281630f31c69300920ed40a3
  artifact: sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67
  note: propagated from a moved ground

- 2026-09-14T19:22:21-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67
  note: re-read after the commit that adds the `merge-renumber` key. The disjointness of the sectioned and plain evidence lists, and the requirement that there be at least one, are both untouched.
- 2026-09-14T20:21:09-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67
  artifact: sha256:222a65392276c0cc61e35fec1bfabd395dee5590c848b57d4303b30b4f3ec738
  note: propagated from a moved ground

- 2026-09-14T20:21:11-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:222a65392276c0cc61e35fec1bfabd395dee5590c848b57d4303b30b4f3ec738
  note: re-read after the commit that fixes what the pre-merge gate found. The section lost a verbatim duplicate of the merge-renumber check, which had been written into it twice; the disjointness of the evidence lists and the requirement that there be one are untouched.
- 2026-09-20T12:55:57-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:222a65392276c0cc61e35fec1bfabd395dee5590c848b57d4303b30b4f3ec738
  artifact: sha256:8b9600914ff906530f6bf2a48e847507f6edc4fd0eea1ebb2d9aae3f7294d2f5
  note: propagated from a moved ground

- 2026-09-20T12:56:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:8b9600914ff906530f6bf2a48e847507f6edc4fd0eea1ebb2d9aae3f7294d2f5
  note: re-read after the commit that adds the `citation-slug` key. The section gained one more check, written like the two beside it and placed after them. The disjointness and non-emptiness checks are untouched.


## References

- src/claims_ledger/config.py · standing · cites-as-live
