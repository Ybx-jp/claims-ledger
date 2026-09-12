---
id: L0226-a-write-decides-from-the-tree-it-appends-to
kind: claim
stated: 2026-09-11T22:03:28-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 571460ecc7b702694e6faffb8bbfeb9660313688b4f7fad09df41fddf0259c96
---

## Assertion

A run that will append verdicts takes its entries from the working tree even when it was asked for the index, so it decides against the tree it is about to write to.

## Scope

metric: which tree the entries of a writing run are read from
cohort: every run of a checker that appends verdicts
condition: what a verdict records of the artifact is read where the comparison is made, and is not this claim's

## Grounds

- code: src/claims_ledger/schema.py § "entries_for" =sha256:d493ec424f9a3dc8b949f0a205bb50423df8b19d2d9f4583cf5c03cbb29a22f2

## Warrant

An append lands in the working tree. A run that decides from the index is asking a tree that does not hold what the run before it just wrote, so it writes the same verdict again, and again: measured on both writers, three runs with no staging between them left three copies of one verdict, and nothing in either checker noticed. The flag is still worth asking for on such a run, because what the verdict records of the artifact is read where the comparison is made, and recording the working tree's state would be a drift nobody staged. So the two questions are separated rather than the flag refused: which entries, from the tree that will change; what they say about the artifact, from the tree the run was asked about. One function because the rule has four call sites, and a rule written out four times is a rule three of them can drift from.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
