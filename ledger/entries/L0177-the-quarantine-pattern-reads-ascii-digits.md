---
id: L0177-the-quarantine-pattern-reads-ascii-digits
kind: claim
stated: 2026-09-08T18:54:46-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 8053bbf5f2e4c62080f6c4aae443dc1087aad326bca640b4e08aaab51464580d
---

## Assertion

The digits of a quarantined id are ASCII, so a configured prefix followed by fullwidth or
Arabic-Indic digits is not read as a breach of the archive.

## Scope

metric: whether a prefix followed by non-ASCII decimal digits is reported as an archived id
cohort: configured documents, in projects that quarantine a series
condition: the prefix is one the project quarantines and the digits are Unicode decimals outside ASCII

## Grounds

- code: src/claims_ledger/schema.py § "archived_id_re" @34e1bf7da1ee0807955e3508ed131518672ac517
- entry: L0045-an-archived-series-is-refused-by-prefix · distinguishes

## Warrant

ID_RE mints `[0-9]{4}` and nothing else, so there is no id a quarantined series could hold
whose digits are fullwidth or Arabic-Indic, and a pattern that matched them was reporting a
breach of an archive that cannot contain the thing it named. `\\d` matches every Unicode
decimal digit and is what the pattern used; `[0-9]` is what the schema mints. This narrows the
alphabet and leaves the width alone: three digits or more still fire, because L0045's rule is
that an id a digit wide of the schema is still a citation of the archive, and that is a claim
about width rather than about script. The rest of the package already read ASCII here — the
same confusion in a credence is L0149 — so what this fixes is one pattern out of step with its
own package.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
