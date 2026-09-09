---
id: L0167-the-neighbour-count-is-recomputable
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: e6bc9a120fec4101a0b984ca791c24da05ede0476dab4130de30a9f345bc3cf6
---

## Assertion

The number of neighbours every entry has is asked of the installed package rather than written down, by the same code that answers the lookup for one entry.

## Scope

metric: whether the distribution the lookup is judged on can be recomputed from the shipped package
cohort: the neighbours command and the function behind it
condition: any ledger the command can open

## Grounds

- code: src/claims_ledger/neighbours.py § "count" @aadceb0aba82a85fe71b15394896c43977751709
- code: src/claims_ledger/cli.py § "cmd_neighbours" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

count calls the same find the single-entry lookup calls, once per entry, so the summary and the answer cannot disagree about what a neighbour is; cmd_neighbours prints the median, the mean, the largest and how many entries have none. A number about how noisy a heuristic is decides whether it is worth running, and one written into prose is a number that stops being true on the next entry and says nothing about anybody else's ledger.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/neighbours.py · standing · cites-as-live
