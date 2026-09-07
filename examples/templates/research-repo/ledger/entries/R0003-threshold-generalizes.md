---
id: R0003-threshold-generalizes
kind: hypothesis
stated: 2026-09-06T09:10:00-07:00
author: main
grade: argued
credence: 0.55
resolves_when: the preregistered pilot-b threshold sweep resolves
supersedes: none
verbatim_sha: 0
---

## Assertion

The 0.72 threshold will preserve both error-rate margins when transferred from pilot-a
to pilot-b.

## Scope

metric: false-review rate at most 0.16 and miss rate at most 0.07
cohort: synthetic pilot-b rows
condition: scoring model and review policy held fixed

## Grounds

- entry: R0001-threshold-balances-review-errors · cites-as-live
- entry: R0002-review-latency-stays-low · cites-as-live

## Warrant

The first pilot leaves margin on both rates and the latency prediction implies adequate
review capacity. Falsified if either preregistered pilot-b error rate exceeds its margin.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

- ROSTER.md · standing · cites-as-live
