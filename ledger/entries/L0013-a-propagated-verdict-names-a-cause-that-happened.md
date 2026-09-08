---
id: L0013-a-propagated-verdict-names-a-cause-that-happened
kind: claim
stated: 2026-09-07T22:47:42-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 83d01242691b5732f2a815ba3db432c060edac2457f2d8d90446c98818c03590
---

## Assertion

A contested verdict written by the propagation author is checked back against the cause it names, and one whose cause does not exist, has not fallen, or does not name the entry carrying the verdict is reported as an orphan.

## Scope

metric: the reports propagate returns for a verdict by the propagation author whose evidence is an entry pointer
cohort: contested verdicts carrying a fallen or a challenges act
condition: the ledger as loaded, whatever wrote the verdict

## Grounds

- code: src/claims_ledger/propagate.py § "run" @e80ad36e50c2c2a2afab6603592ff5fb1818f89e

## Warrant

run's second pass walks every entry's verdicts and keeps those by the propagation author whose evidence is an entry pointer. For a fallen act it requires the named entry to exist, to hold a fallen status, and to be cited cites-as-live in the carrier's own Grounds; for a challenges act it requires the named entry to carry a challenges act back against the carrier. Anything else is reported fail, naming which of those conditions is the one that does not hold.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
