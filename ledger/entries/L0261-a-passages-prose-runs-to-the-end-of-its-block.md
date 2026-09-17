---
id: L0261-a-passages-prose-runs-to-the-end-of-its-block
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: dd234f594aa21a06bdc92f44bb1c1c712fcc086e13c0d987c8d1a1c2756269c6
---

## Assertion

The prose of a passage runs from its passage line to the end of the block, so no field may follow it.

## Scope

metric: where a passage block ends
cohort: the parse of a Passages section
condition: a block whose prose contains lines shaped like fields

## Grounds

- code: src/claims_ledger/schema.py § "_parse_passages" =sha256:16f188b88a950356de096d3c947d1b5eca8df27597586a7bb46f06518e3e134e

## Warrant

Blocks split on a `- ` at column zero, which is why a stored prose line carries the format's indent. Reading the prose to the end of the block is what lets it contain anything at all; a field after it could not be told from the text, so there is none.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
