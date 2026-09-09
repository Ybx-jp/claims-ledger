---
id: L0185-the-harness-installs-without-a-ledger
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: cff4149820e0d7fc4351a64ee7a302f9f3cadeb5ec6305ac6f81dbbfcfc26b09
---

## Assertion

The harness installer runs without opening a ledger, so a project that has not got one yet can install the hooks and skills.

## Scope

metric: whether the installer requires a ledger to be configured
cohort: every run of the harness installer
condition: the project may have no configuration file at all

## Grounds

- code: src/claims_ledger/cli.py § "cmd_harness" @52859264d2caa6d447021f4cda3c8b26e7d72c1f
- code: src/claims_ledger/cli.py § "NO_LEDGER" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

The command is dispatched from the set that opens no ledger, alongside the scaffolder and the corpus runner. The hooks are part of what tells a session the ledger exists, so an installer that failed on a missing configuration would be demanding the very thing it is there to help set up.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
