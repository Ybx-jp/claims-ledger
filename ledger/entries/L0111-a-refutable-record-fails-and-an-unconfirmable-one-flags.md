---
id: L0111-a-refutable-record-fails-and-an-unconfirmable-one-flags
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 4b2b83de08a3a6a11a40a81abfd9661842a409f4308a27f2b93a2945750ebf8f
---

## Assertion

A propagated verdict whose record version control can refute fails, and one it can only fail to confirm flags.

## Scope

metric: the outcome for each of the two ways a recorded artifact is not confirmed
cohort: propagated verdicts over a ground that now reads fresh
condition: an ordinary drift may be recorded and then abandoned before it is committed

## Grounds

- code: src/claims_ledger/freshness.py § "orphans" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
- code: src/claims_ledger/freshness.py § "caused" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

caused separates the two and orphans gives them different outcomes. A record version control can refute — the pin's own blob, which states no drift, or a marker of absence over a history holding no deletion — is the pre-emptive forgery the rule was written for, and it fails. A record it can only fail to confirm is what an ordinary drift looks like when it is never committed: the run records the working-tree blob, the ledger is committed, and the edit is abandoned. Failing that left a permanent red no legal edit could clear, since verdicts append and only append, the pin is frozen, and nothing is appended for a ground that is fresh. The flag does not soften the forgery rule, because a verdict nothing can confirm cannot silence a drift either.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
