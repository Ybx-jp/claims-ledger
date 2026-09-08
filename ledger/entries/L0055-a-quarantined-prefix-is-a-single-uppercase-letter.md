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

## References

- src/claims_ledger/config.py · standing · cites-as-live
