---
id: R0012-latency-and-error-rates-non-comparable
kind: claim
stated: 2026-09-06T10:10:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0
---

## Assertion

The latency statement and error-rate table produce one directly comparable measurement.

## Scope

metric: joint latency and classification-error value
cohort: synthetic pilot-a
condition: threshold fixed at 0.72

## Grounds

- experiment: experiments/threshold.csv @@BASE@

## Warrant

The table contains error rates but not latency, so the attempted joint comparison was
later judged non-comparable.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-06T10:15:00-07:00 · non-comparable · grade: measured · author: main
  evidence: source: latency-paper · demonstration cohort
  note: the source and table report different metrics

## References

