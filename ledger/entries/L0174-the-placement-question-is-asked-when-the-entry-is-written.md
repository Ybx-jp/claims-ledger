---
id: L0174-the-placement-question-is-asked-when-the-entry-is-written
kind: claim
stated: 2026-09-08T16:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 5335dacf652d83a1ef916119a628f038c13df7dfa970f3aa55ee82f6a17cd1fd
---

## Assertion

The placement of a citation is reported by the command that fingerprints the entry — the earliest point at which the entry's grounds and the citation both exist — and that report changes no exit code.

## Scope

metric: whether the placement of an entry's citations is reported at authoring time, and what the command exits with
cohort: the sha command over one entry
condition: the project has configured the rule on

## Grounds

- code: src/claims_ledger/cli.py § "say_where_the_citation_sits" @abb827e3cd4a443f4cc9e90f1db52a3d5c853622
- code: src/claims_ledger/cli.py § "sha_one" @abb827e3cd4a443f4cc9e90f1db52a3d5c853622

## Warrant

sha_one calls it on the two paths where the fingerprint is settled and returns the code it already returned, so what the command exits with still answers whether the fingerprint was written and nothing else; a second meaning on that code would make a script reading it wrong about the first. The moment is the earliest one available: an entry's citation is written in the commit before the entry, so until the Grounds exist there is no section for the citation to be outside of, and the fingerprint is the step between the two. It asks references for the answer rather than deciding for itself, so the report a person gets here and the report that refuses the commit cannot differ.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
- README.md · standing · cites-as-live
