---
id: L0077-the-registrys-last-byte-is-read-as-one-byte
kind: claim
stated: 2026-09-08T02:26:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 608bb7b6c35155f47dfa27c8ae4506ffeabd1cb7aa5259c8992571c86e8a0efc
---

## Assertion

The registry's final byte is read as one byte rather than by reading the file.

## Scope

metric: how much of the registry is read to decide whether it ends in a newline
cohort: every append to the source registry
condition: a project may hold thousands of source rows

## Grounds

- code: src/claims_ledger/authoring.py § "_ends_in_a_newline" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

_ends_in_a_newline seeks to the end and reads a single byte. The question is asked on every append, and a project with a large registry would otherwise read the whole file each time to learn one byte of it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
