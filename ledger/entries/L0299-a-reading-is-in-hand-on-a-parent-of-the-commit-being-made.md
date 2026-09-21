---
id: L0299-a-reading-is-in-hand-on-a-parent-of-the-commit-being-made
kind: claim
stated: 2026-09-20T17:41:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 4ef0e267b1b5c87c9e470457df16d86be6990b831c6d446558e22c659da9f9cc
---

## Assertion

A corroborating verdict pinned at a commit counts as the latest reading of its ground when that commit is in the history the commit about to be made will have, which mid-operation is HEAD and the incoming side alike.

## Scope

metric: whether a reading pinned on the incoming side sets the effective pin
cohort: a ground compared from its latest corroborating verdict, anchored at a commit
condition: a merge, cherry-pick, revert or rebase is open, and the reading is on the side being brought in

## Grounds

- code: src/claims_ledger/freshness.py § "readings" =sha256:a04fe269f38fa29ec066e8ec44a842e6abba3a3859c09e807658cf0e4cc56de7
- code: tests/test_merge_in_progress.py § "test_a_reading_the_incoming_side_committed_still_sets_the_effective_pin" =sha256:be1d2c6d2fa53ae33063d50898d78996edc8a11e936c00bcd876035dbc1e2b10

## Warrant

`readings` is where a corroborating verdict is accepted or passed over, and the gate it applies is the whole of the rule: a reading has to be a real object, strictly after the ground's own commit, and in this history. That last clause asked `HEAD` and nothing else, and `prospective_revs` is what it asks now — HEAD together with the heads of an operation in progress, which are precisely the parents the commit being made will have.

Narrow, and narrow on purpose. Every ref would let a reading on a branch nobody merged — an abandoned draft still sitting on a remote-tracking ref — move the effective pin of an entry that branch never landed, which is the over-reach the gate exists to prevent. A commit that is about to become a parent is a different thing from a commit that merely exists.

The test states the differential rather than the mid-merge value, and that is what makes it hold something. Measured: with the gate on HEAD alone, the effective pin was the founding ground while the merge was open and the reading's pin once the merge was committed — same tree, same entry, same verdict list, only reachability changed. Asserting the mid-merge value would have pinned the bug and had to be rewritten by whoever fixed it; asserting that the two are equal cannot be satisfied by the broken code and needs no rewriting by the fix.

The consequence while it stood was a ground compared against the text it was established on rather than the text the latest reading moved it past — drift reported that a reading had already discharged, at the moment a merge is being resolved. It fails closed rather than open, which is why it was the quieter of the two.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
