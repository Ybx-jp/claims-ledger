---
id: L0186-an-install-that-changed-nothing-exits-zero-and-one-that-skipped-does-not
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 2d00b2abd8bf24aa494e302ff8ec3b9b744c1b02ea406836fe08906e4401e159
---

## Assertion

An install that changed nothing because everything was already in place exits zero, and one that left a file alone does not.

## Scope

metric: the exit code of an install, against what it actually did
cohort: every run of the harness installer
condition: a re-run of the same install, and a run over a file somebody has edited

## Grounds

- code: src/claims_ledger/cli.py § "report_install" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

Three states carry three meanings: something was written, the same bytes were already there, or something else was and was left alone. Running the command twice is not an error, so an install that only found what it would have written exits zero; an install that left a file alone exits non-zero, because the project does not have what it asked for and reporting success would be the one report this tool must never print.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
