---
id: L0097-credence-and-resolves-when-are-omitted-rather-than-guessed
kind: claim
stated: 2026-09-08T02:30:58-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: e2ef6fe980908c30bc39dd15a5a3d9d78ba8e0e446b3ad39379aea6394a578bd
---

## Assertion

credence and resolves_when are required of a prediction and a hypothesis, and are refused on a claim rather than defaulted onto one.

## Scope

metric: the outcome for a missing credence on a prediction, and for one present on a claim
cohort: entries of every kind
condition: a credence is a plain decimal between zero and one inclusive

## Grounds

- code: src/claims_ledger/validate.py § "check_frontmatter" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_frontmatter requires both fields on a prediction and a hypothesis and fails a claim carrying either, then holds a credence that is present to being a plain decimal in range. A credence nobody stated is a number the ledger would go on to report as though somebody had; omitting it is the honest shape for a claim about what is, which the ledger settles by evidence rather than by a stated probability.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
