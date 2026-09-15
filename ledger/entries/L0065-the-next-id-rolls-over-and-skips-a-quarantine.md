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

- 2026-09-14T19:02:18-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "next_id" @c9f052af09e01b65a2adde51e941ebf24671dcaa
  artifact: sha256:a5266e51a2e0e6ce6f5624e3b64305245f428ba2642437e8e7efdf8e5112e577
  note: propagated from a moved ground

- 2026-09-14T19:02:42-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "next_id" =sha256:a5266e51a2e0e6ce6f5624e3b64305245f428ba2642437e8e7efdf8e5112e577
  note: re-read after the commit that allocates above the whole repository. The section now folds a `reserved` set of ids the repository holds elsewhere into the same numbers it already read off the entries, and nothing else in it moved: the letters are still filtered by the quarantine, the active series is still the highest in use among them, and the rollover to the next letter past 9999 is the same arithmetic on the same set. What this claim asserts about rolling over and skipping a quarantine is untouched.

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
