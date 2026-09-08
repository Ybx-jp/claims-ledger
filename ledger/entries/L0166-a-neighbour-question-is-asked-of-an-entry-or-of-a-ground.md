---
id: L0166-a-neighbour-question-is-asked-of-an-entry-or-of-a-ground
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: ab8cac701192ef2efc2b5cd6d4dc09f8d88850260823f799d64383c78861d9d0
---

## Assertion

The lookup takes an entry id, a path to an entry, or a ground pointer written as an entry would write it, and refuses anything else by name.

## Scope

metric: which arguments the lookup accepts and what it does with one it does not
cohort: the target argument of the neighbours command
condition: a ledger that opened

## Grounds

- code: src/claims_ledger/neighbours.py § "subject_of" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

subject_of matches the argument against every entry's id, path and filename, then hands it to parse_pointer and accepts the result when its type is a declared evidence type, and raises a LedgerError naming the argument otherwise. The pointer form is what an author has before the entry exists: the grounds are being chosen, and there is nothing yet to look the question up by. A pointer subject has no cohort to nest and no relation to report, and the result says only what shares its span.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/neighbours.py · standing · cites-as-live
