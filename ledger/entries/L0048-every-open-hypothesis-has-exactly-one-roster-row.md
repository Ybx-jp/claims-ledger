---
id: L0048-every-open-hypothesis-has-exactly-one-roster-row
kind: claim
stated: 2026-09-08T02:08:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 43bbfbb08a0f68599fb39b717bccd16feb0cc97b98a84f3b43753db61cc50f88
---

## Assertion

Every hypothesis whose status is not terminal is cited by exactly one row of the roster document; a hypothesis with no row and a hypothesis with two both fail.

## Scope

metric: the number of roster rows required to cite each non-terminal hypothesis
cohort: entries of kind hypothesis whose derived status is not terminal
condition: the configuration names a roster document

## Grounds

- code: src/claims_ledger/references.py § "check_roster" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487
- code: src/claims_ledger/references.py § "roster_rows" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487

## Warrant

check_roster collects the rows of every roster document through roster_rows, which recognizes a row by a citation in its opening cell, and then walks the entries themselves: an open hypothesis matched by nothing is reported, and one matched more than once is reported with the count. The roster is maintained by hand rather than generated, so this correspondence is what keeps it honest, and a duplicated row is the shape in which a stale status survives an edit to its twin.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/references.py · standing · cites-as-live
