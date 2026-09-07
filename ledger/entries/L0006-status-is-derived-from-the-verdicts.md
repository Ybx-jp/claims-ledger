---
id: L0006-status-is-derived-from-the-verdicts
kind: claim
stated: 2026-09-07T13:30:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 668604f443c516b9681e8886f9361d5052602aca860bdf3520263382e9369c0d
---

## Assertion

An entry's status is derived by walking its verdict list from open to the last legal verdict, with a terminal verdict stopping the walk.

## Scope

metric: the derived status of an entry
cohort: every entry
condition: the verdict list as parsed, including an empty one

## Grounds

- code: src/claims_ledger/schema.py § "derive_status" @4023af4006273319aec9ae2512d197e4a99fce8c

## Warrant

derive_status starts at open, skips malformed verdicts, stops moving at a terminal status except for the one superseded verdict that may follow refuted or non-comparable, and returns the result rather than reading a stored field.

## Backing

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- README.md · standing · cites-as-live
- src/claims_ledger/schema.py · standing · cites-as-live
