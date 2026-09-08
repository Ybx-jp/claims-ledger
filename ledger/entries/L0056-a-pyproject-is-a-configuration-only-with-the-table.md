---
id: L0056-a-pyproject-is-a-configuration-only-with-the-table
kind: claim
stated: 2026-09-08T02:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0b4a01417bc1484bbd67fe494bedf4f10f981aa67ba0caf56feb7242d5bd2ed0
---

## Assertion

A pyproject.toml is treated as this tool's configuration file only when it carries a tool.claims-ledger table.

## Scope

metric: whether a pyproject.toml without the table is taken as the configuration file
cohort: directories walked while searching for a configuration
condition: a package may depend on this one without configuring a ledger

## Grounds

- code: src/claims_ledger/config.py § "find_config_file" @72ad99b4a138640f009ee09b911c741f84776135
- code: src/claims_ledger/config.py § "_pyproject_table" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

find_config_file opens each candidate pyproject.toml through _pyproject_table and accepts it only when the table is present. Without that test the search would stop at the pyproject.toml of any Python project in the path, and a package that merely depends on this one would become the project root — the checkers would then run against that directory's ledger, or report that it has none.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/config.py · standing · cites-as-live
