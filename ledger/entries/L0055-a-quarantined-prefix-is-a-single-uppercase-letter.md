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

## References

- src/claims_ledger/config.py · standing · cites-as-live
