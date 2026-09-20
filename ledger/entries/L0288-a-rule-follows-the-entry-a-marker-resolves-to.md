---
id: L0288-a-rule-follows-the-entry-a-marker-resolves-to
kind: claim
stated: 2026-09-20T12:32:18-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 3a9c9d67420511b7f5a7f6e518e3dec7908df96341a817b51dbed11a1bf2f077
---

## Assertion

Every rule downstream of a marker is asked about the entry it resolves to rather than about the spelling of the id it carries.

## Scope

metric: whether a rule fires the same way for the two legal spellings of one marker
cohort: the placement rule, the References agreement, the verbatim-assertion rule, the roster rows, and the marker a lift writes
condition: the marker names the whole id, or the series and number alone

## Grounds

- code: src/claims_ledger/references.py § "misplaced_citations" =sha256:cfe8ab180a63d08218d042819eb9180b708f09e1819e9bac7514e911872fd62c
- code: src/claims_ledger/references.py § "run" =sha256:51cf8c55f336e8fd07780a8e4509a9f7645490b4096cd3531b71f499615e89d7
- code: src/claims_ledger/lift.py § "marker_for" =sha256:cbae04449dfb73e10b0dfd920e15f6ba42d45490dfebccdbeb144e8d30231a70

## Warrant

Two spellings of one id are one citation, so a rule that compared strings would be a rule the choice of spelling could turn off, silently and without a report anywhere. Each of the rules is therefore keyed on the entry: the placement question narrows by the resolved entry rather than by the text, so it is still asked of a marker written in the short form; the set a document's citations are collected into holds the resolved id, which is what the References rows are compared against in both directions and what the verbatim-assertion rule asks whether the document cited; the roster's rows are gathered under the entry, so a row citing the number is that hypothesis's row and not a second one nothing counts; and a lift treats either spelling as the section already citing the entry rather than writing a second marker beside the first.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/references.py · standing · cites-as-live
- src/claims_ledger/lift.py · standing · cites-as-live
