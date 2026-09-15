---
id: L0242-two-entries-may-not-carry-one-number
kind: claim
stated: 2026-09-14T19:19:01-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: f179b8c4bfa977dcfa60a962b250f098930fe506ceaebd9b53f0b585bb34eadf
---

## Assertion

Two entries carrying one number are a failure, reported once for the number and naming every entry that carries it.

## Scope

metric: what validate reports over a ledger holding a duplicated number
cohort: every entry in the ledger, taken together
condition: the entries are compared by number, with the slug set aside

## Grounds

- code: src/claims_ledger/validate.py § "check_numbers" =sha256:84d50e9438dca8fb72303e43c671ccafeb9ee4876612807a9d12d67c75d581d3

## Warrant

check_numbers groups every entry by the number its id carries and reports a failure for each number more than one entry answers to, listing them all in the one report; run calls it over the whole entry set, so the question is asked of the ledger rather than of an entry.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
- docs/OPERATING.md · standing · cites-as-live
