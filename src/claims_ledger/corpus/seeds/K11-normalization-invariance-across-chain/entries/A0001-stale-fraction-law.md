---
id: A0001-stale-fraction-law
kind: claim
stated: 2026-09-02T08:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0050b7c7a139a3105b6eefc7620cc776358ab508f66ae1ed83c5756ef4a074c5
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
- source: fx-paper-a · §3
  speaker: fixture paper A authors
  quote: "The naïve estimator that counts stale neighbours over-ranks hubs."

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-02T10:00:00-07:00 · superseded · grade: measured · author: main
  evidence: entry: A0002-stale-fraction-law-v2 · supersedes

## References

