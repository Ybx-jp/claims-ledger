---
id: L0138-a-heading-inside-a-code-fence-ends-no-section
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 173513eb22a2d7fa84501f8209dfa41fd288d7fa002f5aaff631d3a2ecf42a03
---

## Assertion

A line that would be a section header if it were prose ends no section when it falls inside a fenced code block.

## Scope

metric: whether a header-shaped line inside a code fence bounds a section
cohort: artifacts of any sectioned evidence type
condition: a fence opens on three or more backticks or tildes indented by at most three spaces

## Grounds

- code: src/claims_ledger/schema.py § "section_span" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "fenced_spans" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "CODE_FENCE_RE" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

section_span asks fenced_spans for the fenced regions and skips any match starting inside one, for the opening header and for every candidate end. What counts as a header is therefore settled twice — by the configured pattern, which says which headings end a section, and by the fence rule, which says what is a heading at all. Without the second, a document quoting its own section markers inside an example would cut a pinned section short, and everything after the quotation would go uncompared.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
