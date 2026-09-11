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

- 2026-09-08T09:41:22-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/references.py § "run" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487
  artifact: d6569fb97a267a37b74525a3f5ea5ca18695adc6
  note: propagated from a moved ground

- 2026-09-08T09:50:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/references.py § "run" @5ee55ae6992f10c834510759f026644f42614025
  note: read against the change in commit 5ee55ae, which narrowed the dependent exemption from FALLEN to TERMINAL in that one branch; this claim names a different part of the same section and is unaffected
- 2026-09-08T18:55:01-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "archived_id_re" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487
  artifact: 76bdfa94a51461a3105e33f6b8a3ed6026f1bc8f
  note: propagated from a moved ground

- 2026-09-08T18:58:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "archived_id_re" @34e1bf7da1ee0807955e3508ed131518672ac517
  note: read against commit 34e1bf7 by diffing the section at the pin and at that commit; it differs in exactly two places — a docstring paragraph carrying the citation for L0177, and the digit class narrowed from `\\d` to `[0-9]`. Neither is what this claim says: the pattern still fires on the prefix alone without regard to whether the id resolves, and it still admits three digits or more. ID_RE mints no id whose digits are outside ASCII, so the population the condition names is the same one
- 2026-09-11T03:10:06-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/references.py § "run" @5ee55ae6992f10c834510759f026644f42614025
  artifact: sha256:f70bdd5d1e540e25c19e6de691f1c670b4c121ef585d25c54b0f8304ce9dba26
  note: propagated from a moved ground
- 2026-09-11T03:10:06-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/references.py § "run" =sha256:f70bdd5d1e540e25c19e6de691f1c670b4c121ef585d25c54b0f8304ce9dba26
  note: read against the working tree after run gained a docstring, a `minted` set and a skip for citation-shaped parentheticals whose id this ledger never minted, the placement check appended after the roster check, and one renumbered citation, since the reading at 5ee55ae: the archived-prefix matches are still reported per document before the citation walk and skipped inside it, and the new unminted-id skip leaves archived prefixes to that earlier report; the assertion holds as written.

## References

- src/claims_ledger/references.py · standing · cites-as-live
