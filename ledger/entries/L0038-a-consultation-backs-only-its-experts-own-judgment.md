---
id: L0038-a-consultation-backs-only-its-experts-own-judgment
kind: claim
stated: 2026-09-08T02:02:28-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 13896a6092bd3d826afe0e69a92285da9789fda43c68f153491b9cd781e627e9
---

## Assertion

A Backing block on a consultation-type source fails when its speaker is not the speaker the registry records for that source.

## Scope

metric: whether a consultation-backed block passes with a speaker other than the registered one
cohort: Backing blocks whose registry row has type consultation
condition: the source has a registry row and its bytes are present

## Grounds

- code: src/claims_ledger/resolve.py § "check_quote" @ec82c16045421ce5a6cb71befe8ddbe6067489ae

## Warrant

check_quote compares the block's speaker with the row's before it looks at the quote at all, and returns the mismatch as a failure. A consultation records what one expert judged; attributing it to anyone else rests the entry on a relay, and the report says a relayed result resolves to the primary source or not at all.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
