---
id: L0203-a-record-is-refuted-against-its-anchor-and-confirmed-against-the-tree
kind: claim
stated: 2026-09-10T22:03:59-07:00
author: main
grade: measured
supersedes: L0111-a-refutable-record-fails-and-an-unconfirmable-one-flags
verbatim_change: the cohort widens from verdicts over a ground that reads fresh to every propagated verdict, since the refutable half is asked of a pointer whether or not its ground reads fresh; Backing is unchanged and there is none
verbatim_sha: d8c21c02aeca42b82562ec59e000f3fbdc6c41e433aa91e82ffbd68eecd9b1ef
---

## Assertion

A propagated verdict recording the digest its pointer's anchor names fails as refuted, whether or not the comparison has moved past that pointer, and one recording something this run does not see, on a ground that is fresh where it is compared from, flags as unconfirmable; nothing is asked of history.

## Scope

metric: the outcome for each of the two ways a recorded artifact is not confirmed
cohort: every propagated verdict naming a checked ground
condition: an ordinary drift may be recorded and then abandoned before it is committed

## Grounds

- code: src/claims_ledger/freshness.py § "orphans" =sha256:d96fa97c95eb92bc42112d1200215b73bb53248605acae83b623652ba658a300

## Warrant

orphans compares each record against the digest anchor_digest gives for the pointer the verdict names, and fails the entry when they are equal, since such a record states no drift at all; that is the pre-emptive forgery the rule was written for, and it is asked of every pointer so that a real drift and a later reading cannot carry the accusation away. A record that is neither the anchor nor what this run sees, on a ground that is fresh at the pointer it is compared from, is what an ordinary drift looks like when it is never committed or is undone, and it flags rather than fails, since failing it left a permanent red no legal edit could clear. Asking history whether the record was ever held was what the earlier rule did, and what let a forger launder a record with a commit that edited the artifact and one that put it back.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/freshness.py · standing · cites-as-live
- docs/FRESHNESS.md · standing · cites-as-live
