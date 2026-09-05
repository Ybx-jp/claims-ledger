---
id: A0002-dependent-superseded
kind: claim
stated: 2026-09-02T08:00:00-07:00
author: main
grade: argued
supersedes: none
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

- entry: A0001-stale-fraction-law · cites-as-live

## Warrant

If per-node error is governed by fraction, a budget spent on high-fraction nodes removes
more error per refresh than one spent on high-count nodes.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts
- 2026-09-02T10:00:00-07:00 · superseded · grade: argued · author: main
  evidence: entry: A0003-dependent-restated-on-surviving-grounds · supersedes

## References

