---
id: A0002-fraction-law-fails-under-sum-aggregation
kind: claim
stated: 2026-09-02T10:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 7d64657eb96f6903bd5b841a81aab948a9bcb16064f88a446ba9db9f8dc746fb
---

## Assertion

Under sum aggregation the staleness error grows with stale count and degree; the
fraction law does not hold there.

## Scope

metric: centre-node output L2 error
cohort: star graphs, one SAGEConv layer with sum aggregation, 16-dim
condition: uniform perturbation 0.1

## Grounds

- lab: fixtures/lab-007.md § "Observation" @corpus
- entry: A0001-stale-fraction-law · challenges

## Warrant

Sum aggregation keeps the |N(v)| factor. This challenges A0001's scope line.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

