---
id: L0110-an-orphan-is-asked-of-the-ground-and-not-of-each-verdict
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9e5c30d362635edca2a2cda579ca54436a048e04e22b09995214925681cdf0e4
---

## Assertion

The orphan rule is applied to a ground rather than to each verdict, so an entry may carry more than one propagated verdict against the same ground without the extra one being called a forgery.

## Scope

metric: what the orphan rule is asked of
cohort: grounds carrying propagated verdicts
condition: the documented pre-commit workflow produces a second verdict on one ground

## Grounds

- code: src/claims_ledger/freshness.py § "orphans" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
- code: src/claims_ledger/freshness.py § "propagated_by_ground" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

propagated_by_ground collects the verdicts under each ground as written, and orphans judges the group. What the rule protects is a ground — that a drifted one is never silently fresh — and the hook path legitimately produces two: the run records the staged blob, the author stages one more edit, and the next run appends a verdict naming what was finally committed. The accusation against a refutable verdict is kept even when a truthful sibling stands, because no run of this checker ever writes one recording the blob the pin already has.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
