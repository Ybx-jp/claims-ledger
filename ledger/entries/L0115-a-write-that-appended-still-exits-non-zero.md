---
id: L0115-a-write-that-appended-still-exits-non-zero
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 66710579f17ac1caedbaecba1add321a162b86cd8839330915096dbf2ec2db52
---

## Assertion

A run that appended verdicts exits non-zero, so the appended text is looked at before it is committed.

## Scope

metric: the exit status of a writing run whose findings were all flags
cohort: runs invoked with --write
condition: a moved ground is reported as a flag, which alone would exit zero

## Grounds

- code: src/claims_ledger/freshness.py § "run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

run appends a failure for each entry it wrote to, naming how many verdicts it added. The sibling checker gets this for free, because every block it queues sits beside a failure; here the moved case sits beside a flag, so without this the ledger was modified by machinery and the run exited zero. The specification requires the non-zero exit for exactly that reason: a file in the ledger has just been changed by something other than a person.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
