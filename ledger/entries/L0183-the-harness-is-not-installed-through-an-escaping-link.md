---
id: L0183-the-harness-is-not-installed-through-an-escaping-link
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 07060e7b7236a051bef4b22dd9ae0c3911e41b79d442a1e76fd0511863b1e131
---

## Assertion

Every name an install is about to write is asked where it really leads, and nothing is written through one that leaves the project.

## Scope

metric: whether a write's destination is confined to the project
cohort: every file an install writes, under every agent
condition: any component of a destination may be a symbolic link the project does not control

## Grounds

- code: src/claims_ledger/harness.py § "install" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

The install asks the same containment question the scaffolder and the hook installer ask of their own writes, through the same test rather than a second one that could drift from it. A link planted at any of these paths would otherwise take files outside the project while the report named the path inside it that was never written.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T22:33:12-07:00 · superseded · grade: measured · author: main
  evidence: entry: L0193-a-write-is-confined-to-the-directory-it-belongs-to · supersedes
  note: the installer came to write one file that is not in the project — codex reads hooks only from its own configuration home — so a claim whose cohort is every file an install writes cannot answer confinement against the project root alone. The successor asks it against the directory each name belongs to; nothing about the writes into the project changed.

## References
