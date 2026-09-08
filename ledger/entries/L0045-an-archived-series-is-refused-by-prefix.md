---
id: L0045-an-archived-series-is-refused-by-prefix
kind: claim
stated: 2026-09-08T02:08:33-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: b5efa1919ffafca767876fb136fb7c62a3b3d122efc29b5bfadf179dc582e455
---

## Assertion

A document that names an id belonging to a quarantined series fails on the prefix alone, whether or not an entry with that id exists.

## Scope

metric: whether an archived id in a document is reported without regard to whether it resolves
cohort: configured documents, in projects that quarantine a series
condition: the id may be written with three digits or more

## Grounds

- code: src/claims_ledger/references.py § "run" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487
- code: src/claims_ledger/schema.py § "archived_id_re" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487

## Warrant

archived_id_re builds its pattern from the configured prefixes and matches an id anywhere in the body rather than only inside a citation, and run reports every distinct match before it walks the citations. The archived ids are then skipped in that walk, so a breach is reported once as a breach and does not return as a dangling citation. The pattern admits three digits or more because the rule reads prose a person wrote, where an id a digit wide of the schema is still a citation of the archive.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/references.py · standing · cites-as-live
