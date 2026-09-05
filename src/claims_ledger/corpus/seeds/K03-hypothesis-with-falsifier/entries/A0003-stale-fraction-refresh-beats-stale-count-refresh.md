---
id: A0003-stale-fraction-refresh-beats-stale-count-refresh
kind: hypothesis
stated: 2026-09-02T08:00:00-07:00
author: main
grade: argued
credence: 0.6
resolves_when: experiments/ preregistration of the trigger comparison resolves
supersedes: none
verbatim_sha: 8b21aa0e0db7441b9e73df6bfb970f896df21025bb8eaf02175b2f38dd42294e
---

## Assertion

A refresh trigger ranking nodes by stale fraction will reach a lower mean embedding
error than one ranking by stale count at equal refresh budget, on mean-aggregation
models.

## Scope

metric: mean embedding L2 error against full recomputation at equal refresh budget
cohort: mean-aggregation GraphSAGE on an evolving graph
condition: refresh budget fixed per step; baselines full recomputation, no refresh, naive local refresh

## Grounds

- entry: A0001-stale-fraction-governs-mean-aggregation-error · cites-as-live
- entry: A0002-fraction-law-holds-on-reddit-scale · cites-as-live

## Warrant

If per-node error is governed by fraction, a budget spent on high-fraction nodes removes
more error per refresh than one spent on high-count nodes, which over-selects hubs.
Falsified if the count-ranked trigger matches or beats the fraction-ranked one at any
budget in the preregistered sweep.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References


- docs/ROSTER.md · standing · cites-as-live
