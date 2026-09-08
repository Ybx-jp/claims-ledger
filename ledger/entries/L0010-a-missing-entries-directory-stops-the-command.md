---
id: L0010-a-missing-entries-directory-stops-the-command
kind: claim
stated: 2026-09-07T20:36:54-07:00
author: main
grade: measured
supersedes: L0005-a-missing-entries-directory-stops-the-command
verbatim_sha: 135a8de36c1e21e5ccb933d18b44dea855057a04cb17e4a4e439be039d466eb6
---

## Assertion

A checking command whose entries directory is absent or cannot be listed stops with exit 2 and says nothing was checked, instead of reporting a clean run.

## Scope

metric: exit code and stderr of a checking command
cohort: validate, resolve, references, propagate, freshness and check
condition: no entries directory at the configured path, or one that cannot be listed

## Grounds

- code: src/claims_ledger/cli.py § "guard" @d2789a9e23db0b218b7f84303ef46b574e48d127
- code: src/claims_ledger/cli.py § "cmd_validate" @d2789a9e23db0b218b7f84303ef46b574e48d127

## Warrant

guard asks for the listing error of the entries directory before any checker runs and returns 2 for a missing, non-directory or unlistable one; each checking command, of which cmd_validate is the pattern, returns that code without running its checker.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- README.md · standing · cites-as-live
- src/claims_ledger/cli.py · standing · cites-as-live
