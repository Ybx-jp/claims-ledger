---
id: L0293-two-reaches-because-the-questions-are-different
kind: claim
stated: 2026-09-20T15:23:31-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 7b7c674d8a058172c332b791569af1454352455b3beb557c78d866a8e3a9a752
---

## Assertion

Whether a text can be shown is asked of every commit the repository can reach, and whether a region is fixed is asked of HEAD and the sides of the commit about to be made.

## Scope

metric: which commits a history walk reaches
cohort: the two walks the checkers make over the entries directory
condition: the walk answers whether a text is anywhere, or which commit fixed a region

## Grounds

- code: src/claims_ledger/schema.py § "prospective_revs" =sha256:7aeefbabb1ed5b34a6bb9733a807cac35a8a2b90807defc6f742e6f6a6317d7d
- code: src/claims_ledger/schema.py § "git_history" =sha256:9b955321cb089f1a73a48a3214182c115527f9086cf0f61ebe4a868605ea4c76
- code: src/claims_ledger/validate.py § "check_history" =sha256:a8dc0b278ba056161297d7bfb4a6899f044b8da899aa83d7a8b9599271e9d6f6

## Warrant

The two questions fail in opposite directions, so one reach cannot serve both. Asking whether a text is anywhere, a miss licenses a rewrite of a frozen region, so the reach is as wide as the repository goes and over-reach costs nothing: a text found on a ref nobody merged is still a text that can be shown. Asking which commit fixed a region, the oldest commit the walk lists becomes the entry's creating commit, so a stale branch carrying an abandoned draft would be named as the origin of an entry that landed by another route, and the frozen region would be compared against a version it never had, for as long as that ref existed. Narrow there, and wide here.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- src/claims_ledger/validate.py · standing · cites-as-live
