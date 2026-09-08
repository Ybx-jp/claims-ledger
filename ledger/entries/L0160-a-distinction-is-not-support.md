---
id: L0160-a-distinction-is-not-support
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 3d8ea2dd7299282af840872ba50954e18e4b32ed317bd0ae64c06d9afd937591
---

## Assertion

An entry whose every ground is a distinguishes act is reported, and a distinguishes ground is not one of the entries motivating a hypothesis.

## Scope

metric: whether an entry resting only on distinctions is reported, and which grounds count as a hypothesis motivation
cohort: entries carrying at least one distinguishes ground
condition: the entry is well-formed in every other respect

## Grounds

- code: src/claims_ledger/validate.py § "check_sections" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

check_sections partitions the ground pointers into the supporting ones and the distinguishing ones before either rule reads them, so the same partition answers both questions and they cannot drift apart. A distinction says what an entry is not, and an entry that says only that has stated a difference and rested on nothing; a hypothesis motivated only by a claim it holds itself apart from is a bet with nothing under it. The grade rules read the supporting grounds too, though no distinguishing ground is an evidence ground, so nothing there changes.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
- docs/SCHEMA.md · standing · cites-as-live
- README.md · standing · cites-as-live
