---
id: L0089-measured-requires-evidence-and-asserted-forbids-it
kind: claim
stated: 2026-09-08T02:30:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 038b919947e9072a030ad9fc675f5d8987d18f15f365d5cdf0500a6b287f5c14
---

## Assertion

A grade of measured or above requires an evidence ground, and an asserted grade forbids one.

## Scope

metric: whether grade and grounds are held to each other in both directions
cohort: entries of every grade
condition: the evidence types are whichever ones the project configured

## Grounds

- code: src/claims_ledger/validate.py § "check_sections" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_sections collects the types of the entry's grounds and reports both directions: a measured-or-better entry lacking an evidence ground is told which types would satisfy it, and an asserted entry carrying one is told that an observation is measured. One direction alone would let the grade drift from what the entry actually rests on — upward for a claim with nothing behind it, downward for one whose evidence its grade declines to acknowledge.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
