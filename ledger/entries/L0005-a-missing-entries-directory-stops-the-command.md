---
id: L0005-a-missing-entries-directory-stops-the-command
kind: claim
stated: 2026-09-07T13:30:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 135a8de36c1e21e5ccb933d18b44dea855057a04cb17e4a4e439be039d466eb6
---

## Assertion

A checking command whose entries directory is absent or cannot be listed stops with exit 2 and says nothing was checked, instead of reporting a clean run.

## Scope

metric: exit code and stderr of a checking command
cohort: validate, resolve, references, propagate, freshness and check
condition: no entries directory at the configured path, or one that cannot be listed

## Grounds

- code: src/claims_ledger/cli.py § "guard" @4023af4006273319aec9ae2512d197e4a99fce8c
- code: src/claims_ledger/cli.py § "cmd_validate" @4023af4006273319aec9ae2512d197e4a99fce8c

## Warrant

guard asks for the listing error of the entries directory before any checker runs and returns 2 for a missing, non-directory or unlistable one; each checking command, of which cmd_validate is the pattern, returns that code without running its checker.

## Backing

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-07T20:35:53-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "cmd_validate" @4023af4006273319aec9ae2512d197e4a99fce8c
  artifact: 58799c38582c87607e65b36ee17d8c1cd30561b3
  note: propagated from a moved ground

## References

- README.md · standing · cites-as-live
- src/claims_ledger/cli.py · standing · cites-as-live
