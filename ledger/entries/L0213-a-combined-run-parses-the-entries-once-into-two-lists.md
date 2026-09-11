---
id: L0213-a-combined-run-parses-the-entries-once-into-two-lists
kind: claim
stated: 2026-09-11T13:36:40-07:00
author: main
grade: measured
verbatim_change: assertion no longer fixes how many checkers read each list; Scope and Backing unchanged, so the verbatim fingerprint is the predecessor's
supersedes: L0123-check-parses-the-entries-once-into-two-lists
verbatim_sha: 6a566e46f84fcac9603ba940db4f3a1590b5e8fae425656b1dc8e67e743c64ba
---

## Assertion

A combined run parses the entries once into two lists rather than once per checker: what is staged for the checkers that read the index, and the working tree for the rest.

## Scope

metric: the number of times the entries are parsed in a combined run
cohort: a run of all five checkers
condition: the cached flag makes the two lists differ

## Grounds

- code: src/claims_ledger/cli.py § "cmd_check" =sha256:53b8438426314598a9b19644af57316600850ad078e047ae6a91ac2252d570c8

## Warrant

cmd_check loads the working tree once and, under the cached flag, the index once, then hands each checker the list it should be reading. One list would erase the distinction the cached flag exists to make; five loads would parse every entry five times for no answer that differs. Two is what the difference actually costs. The predecessor said which checkers took which list by counting them — two against the index, three against the working tree — and giving resolve a cached mode inverted the counts while leaving the claim exactly where it was, so the successor names the lists by what decides membership instead.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/cli.py · standing · cites-as-live
