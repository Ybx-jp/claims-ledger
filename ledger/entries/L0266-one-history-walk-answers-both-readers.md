---
id: L0266-one-history-walk-answers-both-readers
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 827173bafd775eacb6572c312c414e21bc037ed9146bfa58e124ff261dbb4fea
---

## Assertion

One walk of the history answers both readers of an anchor: whether some version held the text, and what that version said.

## Scope

metric: how many history walks an anchor and a passage cost
cohort: the search for a version matching a digest
condition: a repository holding both anchored grounds and held passages

## Grounds

- code: src/claims_ledger/resolve.py § "digest_in_history" =sha256:d3c7c028c30c1c1456e5f56bbe7294b8f72ef7e901e31366fc49e700fc00b968

## Warrant

An anchor only has to know the text was there; a lifted passage has to be compared against it. Splitting the walk in two to say so would have moved the citations of the entries already pinned to this section out of the span their grounds name, which is a failure and not a flag.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
