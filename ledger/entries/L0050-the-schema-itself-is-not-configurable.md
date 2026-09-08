---
id: L0050-the-schema-itself-is-not-configurable
kind: claim
stated: 2026-09-08T02:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 5e7d506fded78e5e51cb45cd728d50d4dd0651c2a60a87d5dac587b8d27c4cc1
---

## Assertion

The set of keys a project may configure names only where the ledger sits and what the project calls things; it holds no key that changes a grade, a kind, a status, a citation act, the fingerprint or the immutability rules.

## Scope

metric: what the accepted configuration keys can change
cohort: the keys a configuration table may carry
condition: the schema's own vocabulary is fixed in the package

## Grounds

- code: src/claims_ledger/config.py § "KEYS" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

KEYS is the whole of what a configuration may say, and every key in it names a path, a glob, a local type name, a roster filename, a quarantined prefix or an author. None of them reaches the claims model: grades, kinds, statuses, acts, the fingerprint and the append-only rules are written in the schema and have no key here. A project can therefore rename its own vocabulary without weakening what a claim means, which is the line this package draws between configuration and model.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/config.py · standing · cites-as-live
