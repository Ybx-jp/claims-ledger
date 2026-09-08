---
id: L0163-a-neighbour-shares-a-span-or-nests-a-cohort
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0fba2f6f3f718fd6947b7e6b0a92609cc8c8623c00bef9e9b5247b355261f751
---

## Assertion

An entry is a neighbour when it shares an evidence span with the subject or when one of the two cohorts word sets contains the other, and on no other test.

## Scope

metric: the tests by which an entry is proposed as a neighbour
cohort: every entry the ledger holds
condition: the lookup asked of one entry or of one ground

## Grounds

- code: src/claims_ledger/neighbours.py § "find" @aadceb0aba82a85fe71b15394896c43977751709
- code: src/claims_ledger/neighbours.py § "nests" @aadceb0aba82a85fe71b15394896c43977751709
- code: src/claims_ledger/neighbours.py § "cohort_words" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

find proposes an entry when the shared spans are non-empty or nests answers yes, and nests is set containment in either direction over the cohort words rather than a similarity score above a threshold. Containment is the shape that has actually gone wrong in this ledger — two Scopes naming two nested sets, the narrower read as the wider — and a threshold tuned until it surfaced that shape would be a number chosen to fit the one example it was chosen from. Words of three characters or fewer are dropped before the test, because every cohort holds those and two cohorts would otherwise nest on nothing.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/neighbours.py · standing · cites-as-live
