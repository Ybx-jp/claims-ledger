---
id: L0204-a-reading-anchored-by-value-needs-no-place-in-history
kind: claim
stated: 2026-09-10T22:03:59-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 60dd850986a989a616f8cf8a6b9ecca4010361da2e62acfd817be7a69c04eb0e
---

## Assertion

A corroborating verdict anchored by value is a reading of the ground it names wherever it sits, needing no commit in the history to be placed at, so it can be appended in the same commit as the edit it read.

## Scope

metric: which corroborations count as readings a ground is compared from
cohort: corroborated verdicts naming a checked ground's type, path and section
condition: the verdict's anchor is stated by value

## Grounds

- code: src/claims_ledger/freshness.py § "readings" =sha256:ce77c73637f399271bff6955e1fd063f89e285f90853a4123846d9e8eaa60d2a

## Warrant

readings accepts a matching corroboration whose anchor is stated by value without the placement questions it puts to one anchored at a commit, because the digest is the datum the reading saw, stated in full, and there is nothing a position in history could add to or take from it. A reading at a commit has to be shown to sit on a branch, after the ground's own commit, and at an object rather than a name, since a commit on no branch or one older than the pin would otherwise become the baseline; none of those hazards has a by-value analogue.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-20T17:44:02-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "readings" =sha256:ce77c73637f399271bff6955e1fd063f89e285f90853a4123846d9e8eaa60d2a
  artifact: sha256:3296a19ebfedbff85fe444e74e6449c171a6565cd55f8e2d82593eaabe5d9f5d
  note: propagated from a moved ground

- 2026-09-20T17:45:59-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "readings" =sha256:a04fe269f38fa29ec066e8ec44a842e6abba3a3859c09e807658cf0e4cc56de7
  note: A reading anchored by value still needs no place in history: `if not q.by_value and repo is not None` is unchanged, and every line that moved is inside the branch it guards. The by-reference gate asks HEAD and the sides of an open operation now instead of HEAD alone.

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
- docs/FRESHNESS.md · standing · cites-as-live
