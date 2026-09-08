---
id: L0052-an-evidence-type-cannot-take-a-reserved-pointer-name
kind: claim
stated: 2026-09-08T02:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 2e62a20a3d21177f4c35dc0be4539a8f76874225342d5491091b06c794a2fcde
---

## Assertion

An evidence type declared with a name the schema reserves for a pointer of its own is refused, and the reserved names are listed in the error.

## Scope

metric: the outcome of declaring an evidence type named as a reserved pointer type
cohort: the sectioned and plain evidence type lists
condition: the reserved names are entry, source, search and defect

## Grounds

- code: src/claims_ledger/config.py § "from_table" @72ad99b4a138640f009ee09b911c741f84776135
- code: src/claims_ledger/config.py § "RESERVED_POINTER_TYPES" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

RESERVED_POINTER_TYPES is the schema's own pointer vocabulary, and from_table intersects it with the declared evidence types and raises on any overlap. A project that could name an evidence type `entry` would have written a ground the parser reads as a citation of another claim, so the collision is refused where the name is declared rather than discovered at the entry that used it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:42-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" @72ad99b4a138640f009ee09b911c741f84776135
  artifact: ddafd109dfd34f6f75aed2b26773ec283ee64d71
  note: propagated from a moved ground

- 2026-09-08T14:43:42-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "RESERVED_POINTER_TYPES" @72ad99b4a138640f009ee09b911c741f84776135
  artifact: ddafd109dfd34f6f75aed2b26773ec283ee64d71
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "RESERVED_POINTER_TYPES" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

## References

- src/claims_ledger/config.py · standing · cites-as-live
