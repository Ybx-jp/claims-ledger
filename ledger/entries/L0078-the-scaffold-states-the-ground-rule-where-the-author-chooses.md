---
id: L0078-the-scaffold-states-the-ground-rule-where-the-author-chooses
kind: claim
stated: 2026-09-08T02:26:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 83e9f96e25dfcdcf9114dfdb43be731f04ca2292dcf04124f26734754a42fd24
---

## Assertion

The scaffolded entry states the ground rule in the placeholder an author writes over: the narrowest section that carries the rule, and never a caller that merely follows it.

## Scope

metric: whether the ground rule is stated at the point the author chooses a ground
cohort: entries created by the scaffolding command
condition: the placeholder is the text the author edits

## Grounds

- code: src/claims_ledger/authoring.py § "PLACEHOLDER_GROUNDS" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

PLACEHOLDER_GROUNDS carries the rule as its own text, so it is on screen at the moment the choice is made rather than in documentation the author may have read once. The two failures it names are the expensive ones: a ground wider than the claim goes stale for edits the claim does not name, and a ground on a caller goes stale for every edit to that caller, forever. Each costs a supersession every time.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
