---
id: A0002-dependent-non-comparable
kind: claim
stated: 2026-09-02T08:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d7956a14b9b91fcbe12f4b3d0cb5604331ef27ee43194f5004228cc9a0ee0686
---

## Assertion

At equal refresh budget, ranking nodes by stale fraction removes more embedding error
per refresh than ranking by stale count.

## Scope

metric: mean embedding L2 error against full recomputation at equal refresh budget
cohort: mean-aggregation GraphSAGE on an evolving graph
condition: refresh budget fixed per step

## Grounds

- lab: fixtures/lab-006.md § "Observation" @corpus
- entry: A0001-stale-fraction-law · cites-as-live

## Warrant

If per-node error is governed by fraction, a budget spent on high-fraction nodes removes
more error per refresh than one spent on high-count nodes, and the sweep measures that
ordering directly.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-02T11:00:00-07:00 · non-comparable · grade: measured · author: main
  evidence: lab: fixtures/lab-008.md § "Observation" @corpus
  note: the later sweep changed the aggregation from mean to max, so the two runs answer different questions and the budget result cannot be compared across them

## References
