---
id: L0065-the-next-id-rolls-over-and-skips-a-quarantine
kind: claim
stated: 2026-09-08T02:26:23-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 78d13de2b60876e6c46b12d54186afa71cc201f77412cf2394f4dd83bd78bfee
---

## Assertion

The next id continues the highest series in use, rolls to the following letter when a series is exhausted, and skips any prefix the project has quarantined.

## Scope

metric: the id allocated for a new entry
cohort: projects holding entries in one or more series, with or without quarantined prefixes
condition: a series holds at most four digits

## Grounds

- code: src/claims_ledger/authoring.py § "next_id" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

next_id collects the numbers used under each series letter, picks the highest letter that is not quarantined, and returns the successor of its highest number. Past four digits it moves to the next unquarantined letter after the active one, and raises when there is none rather than minting an id the schema cannot express. Skipping the quarantine at allocation is what keeps a new entry out of a series the project retired, which the reference checker would otherwise report as a breach the moment the entry was cited.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
