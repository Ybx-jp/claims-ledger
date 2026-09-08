---
id: L0049-a-roster-row-states-what-the-entry-says
kind: claim
stated: 2026-09-08T02:08:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 361e95dce7de8635d458bbfaa17ef6de4ff3132d5e52c6b8b720573904267811
---

## Assertion

A roster row is held to the entry its opening cell cites: that entry must be a hypothesis, and the row's closing cell must state the status the ledger derives for it.

## Scope

metric: whether a roster row disagreeing with its entry's kind or status is reported
cohort: rows of a roster document whose opening cell cites an existing entry
condition: the citation resolves to an entry

## Grounds

- code: src/claims_ledger/references.py § "check_roster" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487
- code: src/claims_ledger/references.py § "roster_rows" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487

## Warrant

roster_rows returns each row's cells together with the id its opening cell cites, and check_roster compares the entry's declared kind and the status derived from its verdicts against what the row says, naming both values in the report. The roster is a view a person maintains; holding it to the entries is what keeps a hand-written status from outliving the verdict that changed it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/references.py · standing · cites-as-live
