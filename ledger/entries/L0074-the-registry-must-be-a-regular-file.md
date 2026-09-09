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

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
