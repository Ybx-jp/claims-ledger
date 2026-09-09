---
id: L0126-init-asks-the-containment-question-of-every-name-it-writes
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 4381e9b21d374602cae422bceb334071cb0a2d5441fb41b80329ff5ff3b2327c
---

## Assertion

The scaffolder asks where each of the four names it writes really leads before it writes any of them.

## Scope

metric: whether the containment question is asked of the scaffolder's write targets
cohort: the ledger directory, the configuration, the cache ignore file and the registry
condition: the command creates the root, so it has no configured ledger to inherit a guard from

## Grounds

- code: src/claims_ledger/cli.py § "cmd_init" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

cmd_init resolves the root and then asks, of each of the four paths, whether it leads outside it. Skipping the question because this command creates the root is what let a symlink planted at any of those names send the scaffolder outside the project at exit 0, printing the in-root path it had not written to. The root is resolved first, so the question is answerable here even though there is no ledger yet.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
