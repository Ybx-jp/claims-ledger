---
id: A0010-fraction-law-fails-under-sum-aggregation
kind: claim
stated: 2026-09-02T10:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: c716eb0d2c032450272ccfe47bf9a33488c4383221f788ec2c7390b24358e860
---

## Assertion

Under sum aggregation the staleness error at a node grows with the stale count and with
degree; the fraction law does not hold there.

## Scope

metric: centre-node output L2 error under fixed-magnitude neighbour perturbation
cohort: star graphs, one SAGEConv layer with sum aggregation, 16-dim, eval mode
condition: uniform perturbation 0.1; stale set uniform-random

## Grounds

- lab: fixtures/lab-007.md § "Observation" @corpus
- entry: A0009-stale-fraction-law · challenges

## Warrant

Sum aggregation keeps the |N(v)| factor, so the error scales with count. This challenges
A0009's scope line, not its assertion: the claim is stated for mean aggregation and the
challenge is that its scope must exclude sum aggregation explicitly.

## Backing

- source: fx-paper-b · Theorem 2
  speaker: Okafor and Lindqvist
  quote: "The expander bound tightens under mean aggregation because the normalisation removes the degree factor from the aggregate."

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

