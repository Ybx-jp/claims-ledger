---
id: L0071-a-ledger-inside-another-repository-still-has-a-history
kind: claim
stated: 2026-09-08T02:26:33-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d683beba0f0689c9cc5c81e4eeeb43ebf2e46167de5341358a83c271f875ee08
---

## Assertion

A ledger sitting inside a repository it does not own is still asked about that repository's history, starting from the directory holding the entry.

## Scope

metric: whether an entry's committed state is established when the ledger root is not itself the repository
cohort: ledgers nested inside another project's repository
condition: the ledger itself has no repository recorded

## Grounds

- code: src/claims_ledger/authoring.py § "is_committed" @c9f052af09e01b65a2adde51e941ebf24671dcaa
- code: src/claims_ledger/schema.py § "enclosing_repository" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

With nothing recorded for the ledger, is_committed walks up from the entry's own directory to find the repository that actually holds the file, and answers against that one. Reporting the entry as uncommitted there is what let a fingerprint rewrite edit the frozen region of an entry the surrounding repository had already committed. The walk starts at the entry because the question is about a file; starting at the ledger root instead would have meant editing restamp, whose span another entry pins.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
