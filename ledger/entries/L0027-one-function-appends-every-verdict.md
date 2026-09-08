---
id: L0027-one-function-appends-every-verdict
kind: claim
stated: 2026-09-07T23:17:47-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 2b2227db7500da6a88f0bc608e01fce8a23847c3fc334c084d86a74cab640353
---

## Assertion

Both checkers that write verdicts write them through the same function: freshness reaches its append through the one propagate defines rather than through an append of its own.

## Scope

metric: the number of definitions in the package that insert text into an entry's appendable region
cohort: propagate --write and freshness --write
condition: the package as it ships

## Grounds

- code: src/claims_ledger/propagate.py § "append_verdict" @0af113005f955a4e120d71338993a94cc6efeb7b
- code: src/claims_ledger/freshness.py § "run" @0af113005f955a4e120d71338993a94cc6efeb7b

## Warrant

append_verdict is the definition that performs the insertion, and freshness's run reaches its write through the imported append_verdict and grouped rather than composing one, so the marker guard, the line-ending handling and the root check are established once and hold for both checkers.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
