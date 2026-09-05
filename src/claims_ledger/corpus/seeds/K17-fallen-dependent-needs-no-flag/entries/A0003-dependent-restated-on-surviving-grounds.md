---
id: A0003-dependent-restated-on-surviving-grounds
kind: claim
stated: 2026-09-02T10:00:00-07:00
author: main
grade: argued
supersedes: A0002-dependent-superseded
verbatim_sha: d7956a14b9b91fcbe12f4b3d0cb5604331ef27ee43194f5004228cc9a0ee0686
---

## Assertion

A refresh trigger ranking nodes by stale fraction will remove more error per refresh
than one ranking by stale count on mean-aggregation models.

## Scope

metric: mean embedding L2 error against full recomputation at equal refresh budget
cohort: mean-aggregation GraphSAGE on an evolving graph
condition: refresh budget fixed per step

## Grounds

- lab: fixtures/lab-005.md § "Observation" @corpus
- entry: A0001-stale-fraction-law · cites-as-fallen

## Warrant

The mechanism the lab note measures is the 1/deg weighting; the refuted entry had
stated it under a scope the note does not support, and is cited here only as history.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

