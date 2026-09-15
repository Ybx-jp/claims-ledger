---
id: L0055-a-quarantined-prefix-is-a-single-uppercase-letter
kind: claim
stated: 2026-09-08T02:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 94b1c87df75fe3d541c0a36ed0bc6da740d7329d3e9cedb871a5b3861a17b9a4
---

## Assertion

A quarantined id prefix that is not a single uppercase letter is refused when the configuration is read.

## Scope

metric: the outcome of declaring an archived prefix that is not one uppercase letter
cohort: the archived-prefixes setting
condition: the quarantine is matched against ids by prefix

## Grounds

- code: src/claims_ledger/config.py § "from_table" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

from_table tests each declared prefix for being a string, of length one, and uppercase, and raises naming the value. The quarantine is applied by building a pattern from these prefixes and matching ids anywhere in a document; a prefix of another shape would build a pattern that matches something other than an id, and the breach it is supposed to catch would go unreported while unrelated prose was flagged.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:42-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" @72ad99b4a138640f009ee09b911c741f84776135
  artifact: ddafd109dfd34f6f75aed2b26773ec283ee64d71
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed
- 2026-09-11T03:10:01-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  artifact: sha256:68ac3fee3de92f6a488946f8b0d0e81b3ce87100281630f31c69300920ed40a3
  note: propagated from a moved ground
- 2026-09-11T03:10:01-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:68ac3fee3de92f6a488946f8b0d0e81b3ce87100281630f31c69300920ed40a3
  note: read against the working tree after from_table gained, since the reading at 2a76453, a check that `citation-placement` is one of its three outcomes and passes it into Config: each archived prefix is still tested for being one uppercase letter and refused by value; the assertion holds as written.
- 2026-09-14T19:21:53-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:68ac3fee3de92f6a488946f8b0d0e81b3ce87100281630f31c69300920ed40a3
  artifact: sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67
  note: propagated from a moved ground

- 2026-09-14T19:22:21-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67
  note: re-read after the commit that adds the `merge-renumber` key. The quarantined-prefix check is untouched: a prefix is still refused unless it is a single uppercase letter.
- 2026-09-14T20:21:09-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67
  artifact: sha256:222a65392276c0cc61e35fec1bfabd395dee5590c848b57d4303b30b4f3ec738
  note: propagated from a moved ground

- 2026-09-14T20:21:11-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:222a65392276c0cc61e35fec1bfabd395dee5590c848b57d4303b30b4f3ec738
  note: re-read after the commit that fixes what the pre-merge gate found. The section lost a verbatim duplicate of the merge-renumber check, which had been written into it twice; the quarantined-prefix check is untouched.

## References

- src/claims_ledger/config.py · standing · cites-as-live
