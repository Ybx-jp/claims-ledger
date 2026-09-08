---
id: L0146-why-a-path-is-unreadable-is-said-rather-than-collapsed
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 5d03a945f23ee76b103d34fa8a9dd79f47a7ab95ce042b56a60b46795587196f
---

## Assertion

Why a path is not a readable regular file is reported as which of those things it is, rather than collapsed into a single negative.

## Scope

metric: how many outcomes a path check distinguishes
cohort: entries, registries and the files a pointer names
condition: interpreters differ in how they surface a permission error here

## Grounds

- code: src/claims_ledger/schema.py § "file_problem" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

file_problem calls stat directly and separates a path that is absent, a link pointing at nothing, a path that could not be read at all, and something present that is not a regular file. The convenience test answers a plain no to every one of those, and the difference between them is the difference between a message someone can act on and an apology about an unexpected error. It also answers differently by interpreter version — one lets the permission error out, another swallows it — while the system call underneath says the same thing everywhere.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
