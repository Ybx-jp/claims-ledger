---
id: L0084-the-whole-history-costs-three-git-processes
kind: claim
stated: 2026-09-08T02:30:49-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 893c84b73b5944d9c6dcfb6b8be225579186311e4021da89caa3f64f2ce5b1f1
---

## Assertion

The whole ledger's history is read with three git processes: one asking whether anything is committed, one walk of the entries directory, and one batch reading every blob the walk named.

## Scope

metric: the number of git processes a history check starts
cohort: a validate run over a ledger of any size
condition: the count is expected to stay flat as entries and revisions grow

## Grounds

- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/schema.py § "git_history" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/schema.py § "git_blobs" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_history asks rev-parse once, calls git_history once over the entries directory rather than once per entry, and hands every wanted blob specification to git_blobs, which reads them in a single cat-file batch. The walk was the part that scaled worst: git log against one path visits every commit however few touched it, so a per-entry loop cost the product of entries and commits. Three is a constant, and it is the constant that keeps a pre-commit hook usable as the ledger grows.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
