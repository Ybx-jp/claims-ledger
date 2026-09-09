---
id: L0058-a-table-keeps-working-when-it-leaves-pyproject
kind: claim
stated: 2026-09-08T02:13:07-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d66df196a758deb8e22b2540d8de9fe52ab0090dcdffbbf5f1f18e1b6a5fbf49
---

## Assertion

A configuration table is read from a standalone file whether its keys sit at the top level or under a tool.claims-ledger table, so a table lifted out of a pyproject.toml keeps working where it lands.

## Scope

metric: whether a standalone configuration file is read under both key layouts
cohort: claims-ledger.toml and .claims-ledger.toml
condition: the file parses as TOML

## Grounds

- code: src/claims_ledger/config.py § "_read_table" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

_read_table looks for the tool table and falls back to the parsed document itself, so both layouts resolve to the same table. Moving a configuration out of a pyproject.toml is the ordinary way a project's ledger settings grow into their own file, and a reader who copies the table across without unwrapping it gets the configuration they wrote rather than a file that parses and configures nothing.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/config.py · standing · cites-as-live
