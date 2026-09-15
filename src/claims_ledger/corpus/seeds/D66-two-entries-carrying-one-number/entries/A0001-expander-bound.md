---
id: A0001-expander-bound
kind: claim
stated: 2026-09-08T08:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 43d27c5a4b4ca46f39364c85adb4156927e2f4f670e344221e34e95840d347f6
---

## Assertion

Under mean aggregation, per-neighbour staleness error on an expander is governed by the stale
fraction of the neighbourhood rather than by the expansion constant.

## Scope

metric: centre-node output L2 error under fixed-magnitude neighbour perturbation
cohort: expander graphs, one SAGEConv layer, 16-dim, eval mode, untrained weights
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

