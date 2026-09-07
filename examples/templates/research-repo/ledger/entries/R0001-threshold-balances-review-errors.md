---
id: R0001-threshold-balances-review-errors
kind: claim
stated: 2026-09-06T09:00:00-07:00
author: main
grade: preregistered
supersedes: none
verbatim_sha: 0
---

## Assertion

In pilot-a, a threshold of 0.72 keeps the false-review rate at 0.14 and the miss rate at
0.05.

## Scope

metric: false-review rate and miss rate
cohort: synthetic pilot-a rows
condition: threshold fixed at 0.72 before the demonstration run

## Grounds

- experiment: experiments/threshold.csv @@BASE@
- source: latency-paper · demonstration cohort

## Warrant

The preregistered row directly records both rates at the fixed threshold, while the
source independently constrains the operating condition used in the fictional study.

## Backing

- source: latency-paper · demonstration cohort
  speaker: Rao and Bell
  quote: "In the demonstration cohort, the median review latency remained below two minutes at a threshold of 0.72."

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

- README.md · standing · cites-as-live
- ROSTER.md · standing · cites-as-live
