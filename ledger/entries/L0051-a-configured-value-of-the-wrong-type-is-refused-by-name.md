---
id: L0051-a-configured-value-of-the-wrong-type-is-refused-by-name
kind: claim
stated: 2026-09-08T02:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 27fd4f68a72d2c7f2cba74388af388c971d109b0fe4a3744fad6c5fbd1ff35f8
---

## Assertion

A configuration value whose type is not the one its key expects is refused, with the key, the type found and the type wanted all named.

## Scope

metric: the outcome of loading a table holding a value of the wrong type
cohort: every key the configuration accepts
condition: the key is known and its value is present

## Grounds

- code: src/claims_ledger/config.py § "from_table" @72ad99b4a138640f009ee09b911c741f84776135
- code: src/claims_ledger/config.py § "KEYS" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

KEYS carries the expected type beside each key, and from_table walks the whole table checking values against it before it builds anything. The error names the key, the type it found and the types it wanted, so the reader repairs the configuration rather than reading a later failure in a checker that got a string where it expected a list.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:42-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" @72ad99b4a138640f009ee09b911c741f84776135
  artifact: ddafd109dfd34f6f75aed2b26773ec283ee64d71
  note: propagated from a moved ground

- 2026-09-08T14:43:42-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "KEYS" @72ad99b4a138640f009ee09b911c741f84776135
  artifact: ddafd109dfd34f6f75aed2b26773ec283ee64d71
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "KEYS" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

## References

- src/claims_ledger/config.py · standing · cites-as-live
