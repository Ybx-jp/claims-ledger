---
id: L0063-a-configuration-that-cannot-be-read-stops-the-command
kind: claim
stated: 2026-09-08T02:13:07-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: c2e47a5a206ea53cf81420908e831c196786371d343d11aa1a4cbac2c2d40530
---

## Assertion

A configuration file that cannot be parsed, or that an explicit path names and does not exist, stops the command with an error rather than being replaced by defaults.

## Scope

metric: the outcome of a configuration file that cannot be read or parsed
cohort: claims-ledger.toml, .claims-ledger.toml and a pyproject table
condition: the defaults would otherwise be a valid configuration

## Grounds

- code: src/claims_ledger/config.py § "ConfigError" @72ad99b4a138640f009ee09b911c741f84776135
- code: src/claims_ledger/config.py § "_read_table" @72ad99b4a138640f009ee09b911c741f84776135
- code: src/claims_ledger/config.py § "_pyproject_table" @72ad99b4a138640f009ee09b911c741f84776135
- code: src/claims_ledger/config.py § "load_config" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

Each read path converts its failure into a ConfigError naming the file: an unparsable TOML, a pyproject named directly that carries no table, and a configuration path that names nothing. load_config falls back to the defaults only where the search genuinely found no file. Defaulting past a file that exists and could not be read would leave a checker running under a configuration the project did not write, reporting a clean ledger it never checked the way the project asked.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/config.py · standing · cites-as-live
