---
id: L0254-a-bare-number-is-not-moved-while-an-entry-still-answers-to-it
kind: claim
stated: 2026-09-14T21:04:01-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 7259a3a66f0bdd5eedc5d6e04a832b733f3ebca4016102522d1f19350f32b355
---

## Assertion

A renumber moves a bare number only when no entry still answers to it.

## Scope

metric: which bare numbers a rewrite substitutes
cohort: every number an intra-branch collision moves
condition: another entry keeps the number the moved id carried

## Grounds

- code: src/claims_ledger/renumber.py § "substitutions" =sha256:377ea26f88e1e1b4f955807b740ed0cbef6ea1a7c06a36732a0c4b5261a6ae55

## Warrant

substitutions emits the bare-number pattern only for a number absent from the set of numbers entries still hold after the mapping, which plan computes from the tip; a bare number in prose means the entry that kept it, and no checker reads one, so rewriting it would point every such sentence at the entry that left and nothing would report it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
