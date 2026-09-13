---
id: L0222-a-combined-run-parses-the-entries-once-into-one-list
kind: claim
stated: 2026-09-11T19:40:22-07:00
author: main
grade: measured
verbatim_change: assertion corrected from two lists to one, the predecessor's two having been the consequence of two checkers with no cached mode; Scope narrowed to the count alone
supersedes: L0213-a-combined-run-parses-the-entries-once-into-two-lists
verbatim_sha: 6b96c97f1117ff1fcb9263c253173963f8af34469ddb3049ccd53229d1f6712c
---

## Assertion

A combined run parses the entries once into a single list and gives that list to all five checkers, rather than once per checker.

## Scope

metric: the number of times the entries are parsed in a combined run, and the number of lists made of them
cohort: a run of all five checkers
condition: which tree the list was read from is the cached flag's business, not this claim's

## Grounds

- code: src/claims_ledger/cli.py § "cmd_check" =sha256:d4d8c8f046d661004b189ba95f06aad4b83f6c2e16a436503764fcf1750b4e2b

## Warrant

The parse is the expensive part of a combined run and nothing about it differs between the five checkers, so it is done once. The predecessor claimed two lists, and that was true of it: the reference and propagation checkers had no cached mode, so under the flag they had to be handed the working tree while the other three read the index. Both take the flag now, so the second list has no reader and the run makes one. The claim is about the count and not about which tree it came from, because which tree is the flag's own subject and is claimed where the flag is read.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
