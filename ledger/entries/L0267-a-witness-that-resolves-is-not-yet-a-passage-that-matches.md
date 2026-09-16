---
id: L0267-a-witness-that-resolves-is-not-yet-a-passage-that-matches
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 01a175118c588f7f71c991c81f7ac30510a55170d22468102b3a6d4cda0ec63f
---

## Assertion

A passage is compared against the version its witness found, so prose the artifact never held fails even where the witness resolves.

## Scope

metric: what resolution establishes about a held passage
cohort: a Passages block and the pre-lift version its witness names
condition: an entry whose witness resolves

## Grounds

- code: src/claims_ledger/resolve.py § "resolve_passage" =sha256:9f82d15b344b24d21b8ff3431e2d6d0d00bb95cb1050db6361328452f7a2bbe9

## Warrant

A witness that resolves shows only that the section existed with those bytes, not that the prose on the entry came out of it. The passage must also be a contiguous run of the lines that version held. A held passage that resolves while saying something the artifact never said is the failure this mechanism exists to make impossible.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
