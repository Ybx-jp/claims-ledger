---
id: L0285-the-slug-a-marker-carries-is-configured
kind: claim
stated: 2026-09-20T12:32:12-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: b3b605cb01370ed037481ddab02aeeec5f0ad4903347ecff374033a150fbee63
---

## Assertion

Whether a marker carries the entry's slug is a configured setting with three values, and a project that says nothing is asked nothing about the shape of its markers.

## Scope

metric: whether the slug rule runs, and which shape it asks for, for a project that has not configured it
cohort: the citation-slug setting
condition: any project the package is pointed at

## Grounds

- code: src/claims_ledger/config.py § "CITATION_SLUG_POLICIES" =sha256:17e8aab1e93cf8b36941697cc1fb1e199e4c55a5bdee3f68cb505891efc76df3
- code: src/claims_ledger/config.py § "DEFAULT_CITATION_SLUG" =sha256:0657d1d63941498afde9458eacffa75f4380a041cc89d28ed7c194aa8254fa84
- code: src/claims_ledger/config.py § "from_table" =sha256:8b9600914ff906530f6bf2a48e847507f6edc4fd0eea1ebb2d9aae3f7294d2f5

## Warrant

CITATION_SLUG_POLICIES is the whole of what the setting may be and DEFAULT_CITATION_SLUG beside it is either, which asks nothing; from_table refuses any other value by name rather than reading it as either, so a project that meant to require one shape and mistyped the value is told rather than left with a checker that said nothing. Either is the default because both spellings resolve to the same entry, so a project that has not chosen between them has not been given a rule it did not ask for; and because every marker a ledger already holds passes under it, which is not true of require or of forbid.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/config.py · standing · cites-as-live
- src/claims_ledger/references.py · standing · cites-as-live
- README.md · standing · cites-as-live
