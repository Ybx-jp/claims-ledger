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

## References

- src/claims_ledger/config.py · standing · cites-as-live
