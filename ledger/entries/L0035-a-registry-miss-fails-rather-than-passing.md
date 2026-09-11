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

- 2026-09-10T21:49:35-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
  artifact: 380802d3237b2e0a79b628ddda818b883cf042b5
  note: propagated from a moved ground
- 2026-09-10T21:49:48-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" =sha256:f01906eb76fb139642ae98df2065ca95a93dceb22e3ed5ee178f036c9203d30b
  note: read against the working tree after the anchor-by-value branch was added: the source branch is untouched and a registry miss still fails naming the check that could not run; the assertion holds as written.
- 2026-09-11T02:49:32-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" =sha256:f01906eb76fb139642ae98df2065ca95a93dceb22e3ed5ee178f036c9203d30b
  artifact: sha256:55d28960d1b04ffe2db203a3b19334115b161628741178ffc4ed4882dac5893d
  note: propagated from a moved ground
- 2026-09-11T02:49:51-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" =sha256:55d28960d1b04ffe2db203a3b19334115b161628741178ffc4ed4882dac5893d
  note: read against the working tree after the by-value branch was moved out of resolve_pointer into resolve_by_value: what remains is the unpinned read from the tree, the pinned read out of git, and the entry and source branches, and the failure messages now write the pin as @<pin> since no by-value anchor reaches them; the assertion holds as written.

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
