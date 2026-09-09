---
id: A0001-stale-fraction-law
kind: claim
stated: 2026-09-02T08:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: b55f51c5c6ee9273514437393b1c5cdeae2d2b39f7532bc0db7a8dfe5fd41809
---

## Assertion

Under mean aggregation, per-neighbour staleness error at a node is governed by the stale
fraction of its neighbourhood, not the stale count; at fixed fraction it is degree-
invariant.

## Scope

metric: centre-node output L2 error under fixed-magnitude neighbour perturbation
cohort: star graphs, one SAGEConv layer, 16-dim, eval mode, untrained weights
condition: single layer; uniform perturbation 0.1; stale set uniform-random

## Grounds

- lab: fixtures/lab-005.md § "Observation" @corpus

## Warrant

Mean aggregation weights each neighbour by 1/deg, so a fixed perturbation on a fraction
f of neighbours contributes f times the per-neighbour effect regardless of degree. The
sweep confirms the mechanism to three decimals, so the direction is structural.

## Backing

- source: fx-paper-a · §1
  speaker: fixture paper A authors
  quote: "Under mean aggregation the per-neighbour contribution is scaled by 1/deg, so the error induced by a stale fraction f of the neighbourhood is proportional to f and does not grow with degree."

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

- docs/prereg-digest.md · standing · cites-as-live
