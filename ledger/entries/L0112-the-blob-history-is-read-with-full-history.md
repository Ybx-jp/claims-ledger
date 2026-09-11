---
id: L0112-the-blob-history-is-read-with-full-history
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 734128b137e4664de454d956e8b97e7604d4d87598112db706d57da75c65c2e1
---

## Assertion

The versions an artifact has held between the pin and the tip are read with full history, so a version the walk declined to list cannot turn a discharge into an orphan.

## Scope

metric: whether the history walk can omit a version the path really held
cohort: the check that a recorded artifact was really held
condition: history may hold merges whose simplification would drop a version

## Grounds

- code: src/claims_ledger/freshness.py § "blobs_since" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

blobs_since asks for the raw log of the path with full history, which prints the before and after object id at each commit that changed it, so one call answers what a walk of the history would. The omission being guarded against is the loud one: a version that is not listed makes a truthful discharge look like a verdict naming a cause that never happened, which is a wedge no legal edit clears.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-10T22:05:55-07:00 · refuted · grade: measured · author: main
  evidence: entry: L0203-a-record-is-refuted-against-its-anchor-and-confirmed-against-the-tree · cites-as-live
  note: blobs_since was removed with the rule that needed it: no version the path held between the pin and the tip is read any more

## References
