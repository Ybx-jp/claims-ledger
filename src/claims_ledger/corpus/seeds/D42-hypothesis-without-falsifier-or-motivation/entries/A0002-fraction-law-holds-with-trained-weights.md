---
id: A0002-fraction-law-holds-with-trained-weights
kind: hypothesis
stated: 2026-09-02T08:00:00-07:00
author: main
grade: argued
credence: 0.6
resolves_when: the preregistered two-layer degree-decile sweep on a trained checkpoint resolves
supersedes: none
verbatim_sha: 233da7f43abcc3d8cec9e2506635c40783003bb316c7d4cebad83cf69f84e056
---

## Assertion

With trained weights and two mean-aggregation layers, the error at a fixed stale fraction
will differ by less than the preregistered margin between degree deciles.

## Scope

metric: centre-node output L2 error at stale fraction 0.25, by degree decile
cohort: a pinned real graph, two SAGEConv layers, trained checkpoint
condition: uniform perturbation 0.1; stale set uniform-random

## Grounds

- entry: A0001-stale-fraction-governs-mean-aggregation-error · cites-as-live

## Warrant

The single-layer law composes through a second mean-aggregation layer without
reintroducing a degree factor, and trained Lipschitz constants scale every neighbour
alike.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

- docs/ROSTER.md · standing · cites-as-live
