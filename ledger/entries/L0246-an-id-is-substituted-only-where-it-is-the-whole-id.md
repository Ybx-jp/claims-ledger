---
id: L0246-an-id-is-substituted-only-where-it-is-the-whole-id
kind: claim
stated: 2026-09-14T20:20:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0ca0f500a8930425f05959e3eb532452fedac14991d12fe0f970817f56658603
---

## Assertion

A renumber substitutes an id only where the text is that whole id, and never where it is the front of a longer one.

## Scope

metric: which occurrences of a moved id a rewrite replaces
cohort: every id that is a textual prefix of another id the ledger holds
condition: two ids share a number and one slug begins with the other

## Grounds

- code: src/claims_ledger/renumber.py § "substitutions" =sha256:ddc3911328bdba06f06757f9da961532883243b380d953fcb183d6352299b001

## Warrant

Both patterns end in a negative lookahead refusing a word character and a hyphen, rather than in a word boundary: a slug ends in a word character and a hyphen is not one, so a boundary alone matches the front of a longer id. Measured before the change: substituting A0002-beta for A0003-beta over `id: A0002-beta-claim` produced `id: A0003-beta-claim`.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
