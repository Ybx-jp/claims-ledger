---
id: L0100-an-option-shaped-pin-is-not-read-as-a-refname
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 8fc9353d4816ec64122d8936d98cf36601b579ff2d2b76c88340b5f9453187d3
---

## Assertion

An option-shaped pin is not read as a refname, because the command asked echoes an argument it did not recognize rather than refusing it.

## Scope

metric: whether a pin beginning with a dash is classified as a moving name
cohort: pins written as free text in an entry's grounds
condition: rev-parse --symbolic-full-name echoes unknown double-dash arguments with exit 0

## Grounds

- code: src/claims_ledger/freshness.py § "names_a_ref" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

names_a_ref accepts only what the command is documented to print for a name — a fully qualified ref, or the bare HEAD of a detached head — and treats everything else as git talking about its own command line. Read as a refname instead, an option-shaped pin drew an unstable-pin flag here and a does-not-resolve failure from the resolver: two contradictory names for one defect. Pins are free text in the schema, so a leading dash is one typo away.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
