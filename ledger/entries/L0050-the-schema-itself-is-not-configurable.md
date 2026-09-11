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

- 2026-09-08T14:43:42-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "KEYS" @72ad99b4a138640f009ee09b911c741f84776135
  artifact: ddafd109dfd34f6f75aed2b26773ec283ee64d71
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "KEYS" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed
- 2026-09-11T03:12:11-07:00 · superseded · grade: measured · author: main
  evidence: entry: L0208-the-schema-itself-is-not-configurable · supersedes
  note: KEYS gained citation-placement, a key that names how strictly one check reports rather than where the ledger sits or what the project calls things, so the assertion's account of the keys was short by one kind; re-stated over the table as it now stands, with Scope and Backing unchanged

## References
