---
id: L0258-a-pinned-commit-is-recognised-by-git-rather-than-by-its-width
kind: claim
stated: 2026-09-14T21:13:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 3be2610fb5a96cbc0ebdcbffddd4bde0a58ef15d9810540fae6684a3d1083153
---

## Assertion

A ground stated by reference is recognised by asking version control what its anchor names, rather than by matching a fixed number of hex characters.

## Scope

metric: which by-reference pins the rewrite refusal finds
cohort: every ground and verdict evidence line anchored at a commit
condition: the anchor is an object name; an anchor stated by value names no commit

## Grounds

- code: src/claims_ledger/renumber.py § "pinned_commit" =sha256:d8beaef749c23dfda7d470fe9108413bb857ad16093366d8fc9bec6acd6f75b9

## Warrant

pinned_commit compares the anchor with the commits being replaced and asks rev-parse about anything shorter than a full id, so an abbreviated pin resolves and an id of any width matches. A pattern of forty hex characters finds neither: it misses the abbreviation git log --abbrev prints, and in a sha256 repository a word boundary never falls inside a 64-hex run, so it finds nothing at all.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
