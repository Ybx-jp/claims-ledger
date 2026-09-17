---
id: L0262-an-optional-section-is-required-only-where-it-appears
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 910ab2735403697272ff8d6e11442983aa00c456d25c5d3a24c5aa64ddfe654c
---

## Assertion

An optional section is held to its place in the section order where it appears and is not reported missing where it does not.

## Scope

metric: how a section named in the schema but absent from an entry is judged
cohort: the section-order check
condition: a section registered after entries already exist

## Grounds

- code: src/claims_ledger/schema.py § "OPTIONAL_SECTIONS" =sha256:2c784abb39f419240b6a1262325f7297ca6d2ea4cafba2a3a87abedc911957d4
- code: src/claims_ledger/validate.py § "check_sections" =sha256:5cd3ff2f7254e6cf8752f53073814d200186d4ed05ff60f17b5dfddb8544043c

## Warrant

Every other section of the schema is required of every entry. Registering a new one without this distinction would have failed all 258 entries that predate it, which is not a schema change a ledger can absorb; with it, a new tail section lands on a ledger whose entries have never heard of it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
