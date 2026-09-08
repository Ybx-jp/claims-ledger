---
id: L0003-unknown-configuration-key-is-an-error
kind: claim
stated: 2026-09-07T13:30:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: a3769738b52683168269047825d3f7827df9049cc61efbc651b06355c6f7870b
---

## Assertion

A configuration key the schema does not know is refused by name rather than ignored.

## Scope

metric: the outcome of loading a configuration table
cohort: claims-ledger.toml and the pyproject table
condition: any key outside the known set

## Grounds

- code: src/claims_ledger/config.py § "from_table" @4023af4006273319aec9ae2512d197e4a99fce8c

## Warrant

from_table computes the keys that are not in KEYS before it reads any value, and raises ConfigError listing them.

## Backing

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:42-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" @4023af4006273319aec9ae2512d197e4a99fce8c
  artifact: ddafd109dfd34f6f75aed2b26773ec283ee64d71
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

## References

- README.md · standing · cites-as-live
- src/claims_ledger/config.py · standing · cites-as-live
