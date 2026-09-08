---
id: L0125-a-path-argument-is-read-from-the-current-directory
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: c77bbfe0b6ba93cf1bdd840e8e23d1a85017ed402e62dc8598c3af49368bfe3a
---

## Assertion

A path argument is read from the current directory, and when the same name would also resolve under the project root that is said rather than left to be discovered.

## Scope

metric: where a path argument is resolved from, and whether the ambiguity is explained
cohort: entry paths given to the fingerprint command
condition: the root may point somewhere other than the current directory

## Grounds

- code: src/claims_ledger/cli.py § "sha_one" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

sha_one resolves the path the way every other command-line tool resolves one, and additionally checks whether the same name exists under the configured root, printing where that entry is. With the root pointing elsewhere the same entry named two ways gave two answers and nothing said why, which is the kind of difference a person spends an afternoon on before finding it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
