---
id: L0107-presence-is-asked-of-stat-rather-than-of-is-file
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 68ab8eafdf3a1bc40667397341693ef89f8952937fb9bfac4f3f5615684cfab7
---

## Assertion

Whether an artifact is still present is asked of stat directly, because a file test has two answers where three are needed.

## Scope

metric: how presence is established, and what an unsearchable directory produces
cohort: evidence artifacts read from the working tree
condition: interpreter versions differ in how they report a permission error here

## Grounds

- code: src/claims_ledger/freshness.py § "in_this_run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

in_this_run calls os.stat and separates three outcomes: gone, present as a regular file, and could not be reached. The convenience test collapses the third into one of the first two, and does it differently by version — one raises the permission error out of the checker, which printed nothing and omitted a whole checker from the summary, and another swallows it and answers no, which is a confident report that a file nobody could look at had been withdrawn. A directory or a FIFO where the artifact was is also not an artifact to read, and that is established here rather than guessed at.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T19:39:25-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "in_this_run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
  artifact: e2386c2564c931207a03de464b78a3bae971afac
  note: propagated from a moved ground

- 2026-09-08T19:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "in_this_run" @225f5867b2591ffc5b3020dfe20ca407d81ee06f
  note: read against commit 225f586, which moved `ARCH-AUDIT.md` into `docs/audits/` and rewrote the mentions of it in this section; the section was parsed at the pin and at that commit and compared with comments and docstrings set aside, and the two are identical, so nothing the claim rests on changed

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
