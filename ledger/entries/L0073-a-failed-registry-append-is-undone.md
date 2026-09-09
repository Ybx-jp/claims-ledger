---
id: L0073-a-failed-registry-append-is-undone
kind: claim
stated: 2026-09-08T02:26:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 5fcde334df1ea992eed75c0e3b8daa16cd226f9ee5d97cbab1c378ec8ef76446
---

## Assertion

A registry append that fails partway is undone: the file is put back to the length it had.

## Scope

metric: the state of the registry after an append that raises
cohort: appends to the source registry
condition: the ledger directory may be read-only, and a write may fail partway through

## Grounds

- code: src/claims_ledger/authoring.py § "append_registry_row" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

append_registry_row records the file's size before opening it and, on an operating-system error, truncates back to that length before re-raising as an authoring error. A registry this command could not extend is still a registry, which matters because a half-written row makes every later read fail rather than only the command that failed. A read-only ledger directory is an ordinary condition — a shared checkout, a directory owned by someone else — and is reported as one.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
