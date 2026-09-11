---
id: L0105-a-withdrawn-ground-records-absent-and-the-deletion-is-sought
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: cf26bdb6bde3ea3b42749a4cfd07eeaa3ee35de49c4afe549c595db28d0e6d5d
---

## Assertion

A withdrawn ground records its absence rather than an object id, and the deletion is then looked for in history the way a blob is.

## Scope

metric: what is recorded, and what is later checked, for a ground whose artifact is gone
cohort: verdicts appended for a withdrawn ground
condition: there is nothing left to hash

## Grounds

- code: src/claims_ledger/freshness.py § "seen_at" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
- code: src/claims_ledger/freshness.py § "caused" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

seen_at returns the absent marker when the ground is withdrawn, because the absence is the thing that happened and no hash describes it. caused holds that record to the same standard as any other: it asks for a commit between the pin and here that actually deleted the path, and a marker of absence over a history holding no deletion states no drift at all — which is the pre-emptive forgery the orphan rule exists to catch.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-10T22:05:55-07:00 · refuted · grade: measured · author: main
  evidence: entry: L0198-a-discharge-records-the-digest-this-run-sees · cites-as-live
  note: the deletion is no longer looked for in history: absent is held to the ground in front of the run, and a withdrawal that was undone is unconfirmable rather than confirmed

## References
