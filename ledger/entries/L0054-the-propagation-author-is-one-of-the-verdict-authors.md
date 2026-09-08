---
id: L0054-the-propagation-author-is-one-of-the-verdict-authors
kind: claim
stated: 2026-09-08T02:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 3b96c5313e927973fda81e19907da5f28a26f480f1c2dfb3cde9d932b9b19843
---

## Assertion

A configuration whose propagation author is outside its list of verdict authors is refused.

## Scope

metric: the outcome of naming a propagation author the verdict-author list does not carry
cohort: the propagation-author and verdict-authors settings
condition: the machinery attributes appended verdicts to the propagation author

## Grounds

- code: src/claims_ledger/config.py § "from_table" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

from_table tests membership and raises with both values named. Every verdict propagate and freshness append is attributed to the propagation author, so a configuration that leaves it outside the accepted authors is one where the machinery's own writes would be rejected by the validator the moment they landed — a failure that would otherwise appear as a broken checker rather than as the misconfiguration it is.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/config.py · standing · cites-as-live
