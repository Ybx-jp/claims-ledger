---
id: A0002-fraction-law-holds-on-reddit-scale
kind: prediction
stated: 2026-09-02T08:00:00-07:00
author: main
grade: argued
credence: 0.7
resolves_when: the two-layer degree-decile sweep in a preregistered experiment resolves
supersedes: none
verbatim_sha: 294cefa71feaad80d893f014b8de027092f318b917b90760c5ead48c096f8539
---

## Assertion

At Reddit scale with two SAGEConv layers, the centre-node error at stale fraction 0.25
will differ by less than 20% between degree deciles.

## Scope

metric: centre-node output L2 error at stale fraction 0.25, by degree decile
cohort: Reddit, two SAGEConv layers, 64-dim, trained weights
condition: uniform perturbation 0.1

## Grounds

- entry: A0001-stale-fraction-governs-mean-aggregation-error · cites-as-live

## Warrant

The single-layer law composes through a second mean-aggregation layer without
reintroducing a degree factor; trained weights change magnitudes, not the 1/deg
structure.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

