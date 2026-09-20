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

- 2026-09-14T19:21:54-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "KEYS" =sha256:338957a895fde219735f5b582fcb2096b43cb0cd4ba9f96a2bcfbfc5449b4685
  artifact: sha256:0f1c17e99e8abbaff42e492001acac910b9d1e41f842e5e4573c47c8c9f8f07e
  note: propagated from a moved ground

- 2026-09-14T19:22:21-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "KEYS" =sha256:0f1c17e99e8abbaff42e492001acac910b9d1e41f842e5e4573c47c8c9f8f07e
  note: re-read after the commit that adds the `merge-renumber` key. The new row names a project's own merge-time policy, which is a project's naming rather than the claims model: the grades, kinds, statuses, acts, fingerprint and immutability rules are still absent from this table, which is what this claim asserts.
- 2026-09-20T12:55:58-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "KEYS" =sha256:0f1c17e99e8abbaff42e492001acac910b9d1e41f842e5e4573c47c8c9f8f07e
  artifact: sha256:831fb3c7cad6e8a1e3c36cb29f98cf85367268f60840b4d2cd870c1e09d97394
  note: propagated from a moved ground

- 2026-09-20T12:56:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "KEYS" =sha256:831fb3c7cad6e8a1e3c36cb29f98cf85367268f60840b4d2cd870c1e09d97394
  note: re-read after the commit that adds the `citation-slug` key. The table gained one row, `citation-slug`, whose value may be a string or a list. What it settles is unchanged: the new key names a house style for a marker, not a part of the claims model. The grades, kinds, statuses and acts are still absent from the table.


## References

- src/claims_ledger/config.py · standing · cites-as-live
