---
id: L0074-the-registry-must-be-a-regular-file
kind: claim
stated: 2026-09-08T02:26:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 8b0b950473330ab6642afa325b3b2e9118b8f93dcd22aa209193048b925f7073
---

## Assertion

A source registry that exists and is not a regular file is refused before anything is written.

## Scope

metric: when the registry's file type is checked, relative to the work of registering
cohort: source registration
condition: the registry path may hold a FIFO or a directory

## Grounds

- code: src/claims_ledger/authoring.py § "register_source" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

register_source tests the registry's type before it reads the source, computes a digest or writes any bytes. Opening a FIFO for append blocks until a reader arrives, which inside a commit hook is a wedged commit printing nothing at all; a directory there raises an error that reads as a defect in the tool. Both are conditions a person can see and repair, so they are named as that, and named before the command has done half its work.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-20T18:15:12-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "register_source" @c9f052af09e01b65a2adde51e941ebf24671dcaa
  artifact: sha256:4e030e5d464c017078e96f9c2d6c78bb8d17f9181d63d82776584d1ab4a91e6a
  note: propagated from a moved ground

- 2026-09-20T18:15:26-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "register_source" =sha256:4e030e5d464c017078e96f9c2d6c78bb8d17f9181d63d82776584d1ab4a91e6a
  note: The registry-is-a-regular-file check is byte-identical and still sits above everything, before the read and before either path. What moved is below it.

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
