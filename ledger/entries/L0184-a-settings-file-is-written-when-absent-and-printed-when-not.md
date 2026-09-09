---
id: L0184-a-settings-file-is-written-when-absent-and-printed-when-not
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d4010eec62dc964c25710fcbf1e34d87d8555eceb6018f6ecfc5bec93f6be023
---

## Assertion

The file that has to name the hooks is written when the project has none and is never edited when it has one; the text it needs is printed instead.

## Scope

metric: what an install does to a settings file that already exists
cohort: every agent whose hooks are wired by a file
condition: that file is where people keep their own hooks and permissions

## Grounds

- code: src/claims_ledger/harness.py § "install_wiring" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

A settings file already there is read for the hooks this install would wire and reported as wired or not; it is never rewritten. Merging into it behind its owner would be a change to their harness they did not make. The check is for a script's name rather than the exact path this install would have used, so a project running the copy inside the installed package is recognised as wired rather than told otherwise on every run.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/harness.py · standing · cites-as-live
