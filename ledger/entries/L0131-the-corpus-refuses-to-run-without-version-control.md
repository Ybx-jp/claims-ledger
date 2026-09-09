---
id: L0131-the-corpus-refuses-to-run-without-version-control
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: a612dddd18176b4071d3c097518a9a9b9066128da8628e2c53b0e912c88d3f17
---

## Assertion

The corpus refuses to run without version control, rather than reporting a pass over seeds it never applied.

## Scope

metric: the outcome of running the corpus where git is absent
cohort: the red-team corpus
condition: the history seeds are applied as commits in a temporary repository

## Grounds

- code: src/claims_ledger/cli.py § "cmd_corpus" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

cmd_corpus tests for git before importing the corpus runner and exits with a message saying that nothing was checked. The seeds are what prove the checkers, so a corpus run that reported success over seeds it could not apply would be the failure this package exists to refuse, aimed at the very thing that establishes the rest.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
