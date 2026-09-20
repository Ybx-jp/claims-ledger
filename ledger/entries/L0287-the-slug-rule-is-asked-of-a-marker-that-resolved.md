---
id: L0287-the-slug-rule-is-asked-of-a-marker-that-resolved
kind: claim
stated: 2026-09-20T12:32:16-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: fc490caa501f0e2d871da744f2cc6c6f1901b234a6cc9ac078dbbaf373e94d08
---

## Assertion

The slug rule is asked only of a marker that resolved to an entry.

## Scope

metric: whether a marker is reported for the shape of the id it carries
cohort: the markers in a document the slug setting governs
condition: the marker resolves to an entry, or names one that does not exist

## Grounds

- code: src/claims_ledger/references.py § "slug_shape" =sha256:c63aca2407ee50bb56a4254ecd5e4c2832af08dd3f400d3ae1927f4e5490b01a

## Warrant

A marker naming an entry that does not exist already has a failure of its own, and it is the failure that matters: the id is wrong, and what shape a wrong id should have been written in is not the repair. Reporting both would put a second line in front of the reader for every mistyped id, and a report that has to be read past is a report that teaches its readers to read past it. The rule is therefore reached only on the branch where the lookup returned an entry, which is also the only branch that can name the right spelling in the message.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/references.py · standing · cites-as-live
