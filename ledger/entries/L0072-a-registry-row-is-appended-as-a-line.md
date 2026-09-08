---
id: L0072-a-registry-row-is-appended-as-a-line
kind: claim
stated: 2026-09-08T02:26:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: fe947d1714a5464b05e4b5f5545b38fa13987107cde7973ed5b121efec375021
---

## Assertion

A registry row is appended as its own line: when the file lacks a final newline, one is supplied before the row is written.

## Scope

metric: whether an appended row can be joined onto the row before it
cohort: appends to the JSON-lines source registry
condition: an editor, a script or an interrupted write may leave the file without a final newline

## Grounds

- code: src/claims_ledger/authoring.py § "append_registry_row" @c9f052af09e01b65a2adde51e941ebf24671dcaa
- code: src/claims_ledger/authoring.py § "_ends_in_a_newline" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

append_registry_row measures the file, asks _ends_in_a_newline about its last byte, and prefixes the separator when it is missing. Without that step the new row was glued onto the previous one, both were destroyed, every later command exited 2 reporting something that was not a JSON object, and the run that caused it printed a success line and exited 0.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
