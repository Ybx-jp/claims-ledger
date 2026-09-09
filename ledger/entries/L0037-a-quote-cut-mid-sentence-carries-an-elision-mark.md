---
id: L0037-a-quote-cut-mid-sentence-carries-an-elision-mark
kind: claim
stated: 2026-09-08T02:02:28-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: e05f2660de250a69344defece3dc6e94877caf73c74221f6c3d1b4e9f2720821
---

## Assertion

A quoted span that begins or ends inside a sentence fails unless the quote carries an elision mark on that side.

## Scope

metric: whether a Backing block passes when a quote boundary falls inside a sentence with no elision mark
cohort: Backing quotes whose opening span starts, or whose closing span ends, away from a sentence boundary
condition: the spans themselves are located in the source

## Grounds

- code: src/claims_ledger/resolve.py § "check_quote" @ec82c16045421ce5a6cb71befe8ddbe6067489ae

## Warrant

check_quote examines the source either side of the located extent and requires a sentence-ending character, a paragraph break, or a closing quotation mark that itself follows a stop; a lead or trail elision mark on the quote lifts the requirement for that side. The test is against the source rather than against the quotation, so a quotation cut mid-sentence has to say so instead of reading as a whole one.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
