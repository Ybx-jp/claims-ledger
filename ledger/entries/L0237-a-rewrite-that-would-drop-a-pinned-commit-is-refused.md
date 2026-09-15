---
id: L0237-a-rewrite-that-would-drop-a-pinned-commit-is-refused
kind: claim
stated: 2026-09-14T19:13:42-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 8cee020183aac365599a44ca1d1b21c01d5cb33a277f01489ba5c3dc477eda5c
---

## Assertion

A rewrite is refused, naming the entry and the commit, when a ground on the branch names by reference a commit the rewrite would replace.

## Scope

metric: the refusals a renumber reports before writing anything
cohort: every ground and every verdict evidence line in the branch's entries
condition: the anchor is stated by reference; an anchor by value names no commit and loses nothing

## Grounds

- code: src/claims_ledger/renumber.py § "refusals" =sha256:a706795921d4b54437bbea58e2e29e246a7e6c349a50ca6842c8d0c021039dff

## Warrant

refusals reads every entry the branch tip holds and intersects the object names in them with the commits the rewrite would replace, so a ground whose evidence the rewrite would remove is reported before anything is written, which is the difference between a supersession and a re-read.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
