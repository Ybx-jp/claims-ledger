---
id: L0035-a-registry-miss-fails-rather-than-passing
kind: claim
stated: 2026-09-08T02:02:28-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: bca04c8e4618ffaaec6e8bddb6a23b460b447fad272439e1be82ff103e2c890d
---

## Assertion

A source id the registry does not hold makes the pointer or the Backing block that named it fail, saying the check could not run.

## Scope

metric: the outcome for a pointer or Backing block naming an unregistered source
cohort: source pointers and Backing blocks
condition: the registry itself loads

## Grounds

- code: src/claims_ledger/resolve.py § "Sources" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
- code: src/claims_ledger/resolve.py § "resolve_pointer" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
- code: src/claims_ledger/resolve.py § "check_quote" @ec82c16045421ce5a6cb71befe8ddbe6067489ae

## Warrant

Sources.text answers a missing row with a problem rather than with empty text, and both callers treat a problem as a failure and stop: resolve_pointer reports it for a source pointer, and check_quote reports it and returns before a span is matched. A missing row therefore cannot become an empty haystack in which quotes quietly fail to be found, nor a check that silently had nothing to do.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
