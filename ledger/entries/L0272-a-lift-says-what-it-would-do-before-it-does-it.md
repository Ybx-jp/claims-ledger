---
id: L0272-a-lift-says-what-it-would-do-before-it-does-it
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: ff87f35f2cbc7bd4555e9ab2ed82258b52d2f6d987c7e8b620dea05ccab6f2e2
---

## Assertion

A lift writes nothing unless it is asked to, and the run that is not asked prints what it would take.

## Scope

metric: what a lift does without a write flag
cohort: the lift command
condition: a lift run against any entry

## Grounds

- code: src/claims_ledger/cli.py § "cmd_lift" =sha256:1ab0a161b369f62d2077a8c070b998b59e2aed2767d019dbaf3285dffd8161fb

## Warrant

A lift deletes prose from a project's source. Every other command in this package that writes is asked to; this one deletes rather than substitutes, so the run a person gets by default is the one that only reports, and the reverse patch is available in the same breath as the write.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
- README.md · standing · cites-as-live
