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

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
