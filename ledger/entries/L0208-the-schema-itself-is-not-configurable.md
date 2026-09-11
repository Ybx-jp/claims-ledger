---
id: L0208-the-schema-itself-is-not-configurable
kind: claim
stated: 2026-09-11T03:11:32-07:00
author: main
grade: measured
supersedes: L0050-the-schema-itself-is-not-configurable
verbatim_sha: 5e7d506fded78e5e51cb45cd728d50d4dd0651c2a60a87d5dac587b8d27c4cc1
---

## Assertion

The set of keys a project may configure names where the ledger sits, what the project calls things, and how strictly one placement check reports; it holds no key that changes a grade, a kind, a status, a citation act, the fingerprint or the immutability rules.

## Scope

metric: what the accepted configuration keys can change
cohort: the keys a configuration table may carry
condition: the schema's own vocabulary is fixed in the package

## Grounds

- code: src/claims_ledger/config.py § "KEYS" =sha256:338957a895fde219735f5b582fcb2096b43cb0cd4ba9f96a2bcfbfc5449b4685

## Warrant

KEYS is the whole of what a configuration may say, and every key in it names a path, a glob, a local type name, a roster filename, a quarantined prefix, an author, or the outcome — off, flag or fail — one checker reports a misplaced citation with. None of them reaches the claims model: grades, kinds, statuses, acts, the fingerprint and the append-only rules are written in the schema and have no key here, and the one key that sets a checker's strictness chooses among that checker's outcomes without adding to or renaming them. A project can therefore rename its own vocabulary and choose how loudly one check speaks without weakening what a claim means, which is the line this package draws between configuration and model.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/config.py · standing · cites-as-live
