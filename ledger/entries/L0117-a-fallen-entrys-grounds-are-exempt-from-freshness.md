---
id: L0117-a-fallen-entrys-grounds-are-exempt-from-freshness
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: fb9120b8fcd0e59987b5d50a4b2b8ca849e828d3eb6c31e7fba3377ab0b3e2c3
---

## Assertion

The grounds of an entry whose status is terminal are exempt from the freshness comparison.

## Scope

metric: whether a terminal entry's pinned grounds are compared against the tree
cohort: entries whose derived status is terminal
condition: those grounds are pinned and their artifacts may have moved

## Grounds

- code: src/claims_ledger/freshness.py § "run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

run skips an entry whose status is terminal before comparing any of its grounds. A fallen entry's Grounds record what it was established on, not what anyone should now believe, and flagging them would ask an author to discharge drift under a claim nobody is relying on any more. The reference checker exempts them for the same reason, so the two agree about what a fallen entry's grounds are for.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
  artifact: 7bf8ce83b6bb554674722efe7e644aa962b022ef
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
