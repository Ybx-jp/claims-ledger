---
id: L0102-a-verdict-discharges-only-the-ground-whose-section-it-names
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6cf4cf8c27083c365ca31a0510190c35fc938d35e1f6911d4d169c91078e6f84
---

## Assertion

A propagated verdict discharges only the ground whose section it names, so one verdict cannot silence a second ground on the same file and pin.

## Scope

metric: which grounds a propagated verdict is matched against
cohort: entries carrying more than one ground on one artifact
condition: the pointers differ only in the section they name

## Grounds

- code: src/claims_ledger/freshness.py § "acknowledgements" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

acknowledgements compares type, target, pin and section, and the section is part of a pointer's identity everywhere else in this checker — the scoped comparison reads that span alone, the orphan rule looks a ground up by its raw text, and the report names the section. A comparison that dropped it let one verdict discharge every ground on the file, and verdicts do not expire, so the second drifted ground would have been reported fresh for the life of the entry.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-10T22:05:57-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "acknowledgements" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
  artifact: sha256:aa0304e2fe1925b9c30fede8eed1d3de73ed6d82c46f6498ec8547bd0b77139b
  note: propagated from a moved ground
- 2026-09-10T22:06:17-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "acknowledgements" =sha256:aa0304e2fe1925b9c30fede8eed1d3de73ed6d82c46f6498ec8547bd0b77139b
  note: read against the working tree after freshness began comparing by digest on both sides: a verdict is matched to a ground on type, path, section and anchor, the anchor now in either form; the section still counts, and the assertion holds as written.

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
