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

## References

- src/claims_ledger/harness.py · standing · cites-as-live
