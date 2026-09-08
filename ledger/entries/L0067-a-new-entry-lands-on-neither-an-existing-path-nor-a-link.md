---
id: L0067-a-new-entry-lands-on-neither-an-existing-path-nor-a-link
kind: claim
stated: 2026-09-08T02:26:24-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 75569448574580fc0d52c9e6b7fd7684533e9de9ab5883121b894812bfb7beaa
---

## Assertion

A new entry is refused when its path already holds a file, and refused again when that path is a link leading outside the project, including a dangling one that does not report as existing.

## Scope

metric: whether an entry is created at a path already occupied or pointed away
cohort: the path a new entry would take in the entries directory
condition: a dangling symlink does not answer to an existence test

## Grounds

- code: src/claims_ledger/authoring.py § "create_entry" @c9f052af09e01b65a2adde51e941ebf24671dcaa
- code: src/claims_ledger/authoring.py § "refuse_to_write_outside_the_root" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

create_entry refuses a path that exists, and then asks refuse_to_write_outside_the_root where the path really leads. The second question is the one the first cannot answer: a dangling link fails the existence test, so the refusal steps aside and the write lands wherever the link points. The other two write sites in the package had always asked; this one was clean by accident rather than by a guard, which is not a property to leave resting on an accident.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
