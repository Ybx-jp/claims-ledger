---
id: L0008-a-section-pin-compares-only-its-section
kind: claim
stated: 2026-09-07T13:30:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6aaac6860d4cf84613b0b4900a321ae5920fb945c6594eed535130cc23ed1384
---

## Assertion

When a pinned ground names a section, freshness compares only that section between the pin and the working tree, so an edit elsewhere in the file is not drift.

## Scope

metric: the freshness finding for a sectioned ground
cohort: grounds of a sectioned evidence type
condition: the file differs from the pin

## Grounds

- code: src/claims_ledger/freshness.py § "scoped" @4023af4006273319aec9ae2512d197e4a99fce8c

## Warrant

scoped extracts the named section from both texts through the project's section pattern and reports moved only when the two sections differ after trailing whitespace is stripped.

## Backing

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-07T19:07:57-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "scoped" @4023af4006273319aec9ae2512d197e4a99fce8c
  artifact: 1e704d90edfafe963b29207f148e31869d60917e
  note: propagated from a moved ground

## References

- docs/FRESHNESS.md · standing · cites-as-live
- src/claims_ledger/freshness.py · standing · cites-as-live
