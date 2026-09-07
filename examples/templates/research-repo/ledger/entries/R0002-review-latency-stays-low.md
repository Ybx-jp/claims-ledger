---
id: R0002-review-latency-stays-low
kind: prediction
stated: 2026-09-06T09:05:00-07:00
author: main
grade: argued
credence: 0.7
resolves_when: the preregistered pilot-b run reports median review latency
supersedes: none
verbatim_sha: 0
---

## Assertion

Median review latency in pilot-b will remain below two minutes at the 0.72 threshold.

## Scope

metric: median review latency
cohort: synthetic pilot-b queue
condition: threshold 0.72 and the same staffing envelope as pilot-a

## Grounds

- entry: R0001-threshold-balances-review-errors · cites-as-live

## Warrant

The threshold leaves the review volume within the invented pilot-a envelope, which is
expected to preserve its latency under the stated staffing condition.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

- ROSTER.md · standing · cites-as-live
