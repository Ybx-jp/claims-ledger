---
id: L0057-the-nearest-configuration-at-or-above-the-start-is-used
kind: claim
stated: 2026-09-08T02:13:07-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 09bffc5a08bb54923265ef523475479687eb986377c72e74a88a0eee3f847830
---

## Assertion

The configuration used is the nearest one at or above the starting directory, and a project with none above it gets the defaults rather than an error.

## Scope

metric: which configuration file is chosen when several sit on the path to the root
cohort: the directory the command runs in and its parents
condition: a configuration file may be absent everywhere on that path

## Grounds

- code: src/claims_ledger/config.py § "find_config_file" @72ad99b4a138640f009ee09b911c741f84776135
- code: src/claims_ledger/config.py § "load_config" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

find_config_file walks the starting directory and then its parents in order, returning the moment it finds a file, so a nested project's own configuration wins over an outer one. When the walk finds nothing, load_config returns the default configuration rather than raising: a project that has written nothing down is a project the defaults describe, and refusing it would make the tool unusable before its configuration exists.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/config.py · standing · cites-as-live
