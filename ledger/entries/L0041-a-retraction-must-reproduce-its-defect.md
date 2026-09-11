---
id: L0041-a-retraction-must-reproduce-its-defect
kind: claim
stated: 2026-09-08T02:02:28-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 83c7ba4148a137c02569bb6b9a9837799088fbb0d251e5fbc9c39ee7bfd7c687
---

## Assertion

On a retracted entry the Backing quotes are not re-reported as failures; instead the quote the retraction names is re-checked, and one that still verifies is flagged as a defect that does not reproduce.

## Scope

metric: what a retracted entry's Backing is checked for
cohort: entries whose derived status is retracted and whose verdict carries a defect pointer
condition: the defect names a Backing quote by number

## Grounds

- code: src/claims_ledger/resolve.py § "run" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
- code: src/claims_ledger/resolve.py § "check_retraction" @ec82c16045421ce5a6cb71befe8ddbe6067489ae

## Warrant

run branches on the entry's derived status, sending a retracted entry to check_retraction rather than checking its Backing blocks; the quotes the retraction is about would otherwise be reported again as the very failures the entry already records. check_retraction reads the Backing quote number out of the defect pointer and re-runs check_quote on that block with the relayed-speaker flag suppressed, so what is measured is the stated defect and nothing else. An empty report means the quote verifies, which is flagged, because a retraction resting on a defect that is not there is one a reader cannot confirm. A defect naming no Backing quote, or naming one the entry does not have, is flagged as beyond this checker.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-11T02:49:32-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "run" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
  artifact: sha256:3abb7abd6286ca9b9d146f430c1723b8be318754b5c247bcfcd5369c5df8adc0
  note: propagated from a moved ground
- 2026-09-11T02:49:51-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:3abb7abd6286ca9b9d146f430c1723b8be318754b5c247bcfcd5369c5df8adc0
  note: read against the working tree after resolve began resolving a ground anchored by value from the tree or from history: run now routes such a ground to resolve_by_value, asks once per entry whether git holds it, and passes a by-value reading's own evidence over; the unasked gate is asked once for the ledger before either path and both honour it, and the retraction re-check is unchanged; the assertion holds as written.
- 2026-09-11T03:57:56-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:3abb7abd6286ca9b9d146f430c1723b8be318754b5c247bcfcd5369c5df8adc0
  artifact: sha256:46ff53ce04ef51ab0c8664adc2690f80426a469e4d4df265094310a9c67f133b
  note: propagated from a moved ground
- 2026-09-11T03:58:17-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "run" =sha256:46ff53ce04ef51ab0c8664adc2690f80426a469e4d4df265094310a9c67f133b
  note: read against the working tree after run began passing --cached through to resolve_by_value, so a by-value anchor is held to the index under the hook: the retraction re-check is unchanged; the assertion holds as written.

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
