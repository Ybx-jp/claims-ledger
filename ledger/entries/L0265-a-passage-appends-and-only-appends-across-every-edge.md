---
id: L0265-a-passage-appends-and-only-appends-across-every-edge
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0dd394f6a773cbf4d8d4bff9ac4ba6ecb7d15a77f0f4732bcd17b7ee79b0ab8e
---

## Assertion

Passage blocks are compared across every pair of revisions the way verdict blocks are, so a held passage that is changed or removed fails.

## Scope

metric: what the append-only comparison covers
cohort: the Passages and Verdicts sections across consecutive revisions
condition: the whole history of every entry file

## Grounds

- code: src/claims_ledger/validate.py § "check_history" =sha256:bdbb8276dcecce0f98f63ef837c77d1fc3ce90f757a0b829d7ce222be0926459

## Warrant

A passage sits below the APPEND marker, where the frozen-region comparison does not reach, and the entries directory is not a configured document, so nothing else in the package would notice it change. Without this comparison a held passage could be rewritten or dropped with every checker green, which is the one thing this package exists not to be.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
- docs/SCHEMA.md · standing · cites-as-live
