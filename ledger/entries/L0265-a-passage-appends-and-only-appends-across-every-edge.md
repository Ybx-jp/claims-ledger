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

- 2026-09-20T15:29:17-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_history" =sha256:bdbb8276dcecce0f98f63ef837c77d1fc3ce90f757a0b829d7ce222be0926459
  artifact: sha256:a8dc0b278ba056161297d7bfb4a6899f044b8da899aa83d7a8b9599271e9d6f6
  note: propagated from a moved ground

- 2026-09-20T15:29:43-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_history" =sha256:a8dc0b278ba056161297d7bfb4a6899f044b8da899aa83d7a8b9599271e9d6f6
  note: re-read after the commit that widens the reach of the history walk. The section now passes `prospective_revs` — HEAD and the other side of an operation in progress — where it passed nothing and got HEAD. With no operation under way the walk is the one it was, and the rules this section carries are untouched: what the section refuses is unchanged.


## References

- src/claims_ledger/validate.py · standing · cites-as-live
- docs/SCHEMA.md · standing · cites-as-live
