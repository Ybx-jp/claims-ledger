---
id: L0284-a-marker-names-its-entry-by-id-or-by-number
kind: claim
stated: 2026-09-20T12:32:09-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: a2c4a5e17e58d92b17118c20a653f23e490fe73fac0b70507bc4e07aa664bdbe
---

## Assertion

A citation marker names its entry by the whole id or by the series and number alone, and a marker carrying a slug that is not that entry's names nothing.

## Scope

metric: the entry a marker resolves to
cohort: the markers in a configured document
condition: the marker carries the entry's slug, a different slug, or no slug at all

## Grounds

- code: src/claims_ledger/schema.py § "by_number" =sha256:b3df69a23d3fa04a24558a7543621da68773955082baf2f948544af7ffcf825a
- code: src/claims_ledger/schema.py § "cited_parts" =sha256:d84f1a20bcd6ef27a1e2ad27d3cb188a4d95644b775a473120b522008624c9b0
- code: src/claims_ledger/references.py § "cited_target" =sha256:8f7d1a7910ffcad4366774ecdb2af6054d030f619007faf60b24371e4e775be2

## Warrant

The whole id is looked up first, in the index keyed by it, and only a marker carrying no slug falls back to the index keyed by the number. So the two legal spellings reach one entry, and the third case — a slug the entry does not have, left behind by a rename or mistyped — does not quietly resolve through the number it shares, which is the detection that a number-first lookup would have cost. by_number keys a list rather than an entry because two entries answering to one number is a state a merge produces and validate fails on; cited_target says so rather than picking one of them, since either pick reports a status the reader cannot check. cited_parts splits the marker with partition rather than split, so a trailing hyphen with nothing after it is no slug rather than the empty string that compares equal to none.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- src/claims_ledger/references.py · standing · cites-as-live
