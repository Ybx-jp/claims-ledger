---
id: L0247-a-renumber-re-pins-every-anchor-freshness-may-compare-from
kind: claim
stated: 2026-09-14T20:20:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: c3efcfa1e0503960aa9b607c262f2d7da7813efd9e151ef3cdd7b4dad69ff7ba
---

## Assertion

A renumber re-pins every by-value anchor an entry carries, its verdicts' evidence as well as its Grounds.

## Scope

metric: which of an entry's anchors a rewrite considers
cohort: every by-value anchor of every rewritten entry
condition: the anchor names a sectioned artifact the rewrite also holds

## Grounds

- code: src/claims_ledger/renumber.py § "anchored_pointers" =sha256:2cadeb5d3f0380b0922ef3273b1e5ab3096370dd870e575b28ca3532d1cbe6a8

## Warrant

anchored_pointers returns the Grounds and each verdict's evidence together, and reanchor walks that list; freshness compares a ground from the latest corroborating verdict that names its section once one exists, so an entry whose Grounds alone were re-pinned would be compared from a pointer naming text the rewrite replaced.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
