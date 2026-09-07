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

## References

- README.md · standing · cites-as-live
- src/claims_ledger/config.py · standing · cites-as-live
