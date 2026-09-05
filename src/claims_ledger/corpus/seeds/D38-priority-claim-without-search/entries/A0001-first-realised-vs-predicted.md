---
id: A0001-first-realised-vs-predicted
kind: claim
stated: 2026-09-02T08:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 69dd8e312c5ec3353806067cdd321b563329322be7612f6759d6328840c3f62e
---

## Assertion

This is the first measurement of realised staleness error against the fraction law's
prediction.

## Scope

metric: realised L2 error against the fraction-law prediction
cohort: star graphs, one SAGEConv layer, 16-dim
condition: uniform perturbation 0.1

## Grounds

- lab: fixtures/lab-005.md § "Observation" @corpus

## Warrant

The sweep reports both quantities and the scan of prior work found no such comparison.

## Backing

- source: fx-paper-a · §1
  speaker: fixture paper A authors
  quote: "Under mean aggregation the per-neighbour contribution is scaled by 1/deg, so the error induced by a stale fraction f of the neighbourhood is proportional to f and does not grow with degree."

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

