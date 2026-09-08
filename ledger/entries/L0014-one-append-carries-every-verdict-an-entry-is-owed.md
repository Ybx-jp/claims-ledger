---
id: L0014-one-append-carries-every-verdict-an-entry-is-owed
kind: claim
stated: 2026-09-07T22:47:42-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 788b64f795dd685f7a117622a9b11328bab3f41d78a6c6720dc9d9f999e240a4
---

## Assertion

The verdict blocks one run owes a single entry are joined into one block before any of them is written, so an entry citing two fallen grounds keeps both verdicts rather than having one write over the other.

## Scope

metric: the number of writes, and the number of verdict blocks, a run directs at one entry
cohort: entries owed more than one propagated verdict in the same run
condition: --write over a ledger loaded once

## Grounds

- code: src/claims_ledger/propagate.py § "grouped" @e80ad36e50c2c2a2afab6603592ff5fb1818f89e

## Warrant

grouped keys the pending blocks by the entry's path, keeps them in first-seen order and returns exactly one pair per entry with that entry's blocks joined. Each block is composed from the entry text as it was parsed, so a second write over the same entry would discard the first; returning one pair per entry is what keeps that second write from happening.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
