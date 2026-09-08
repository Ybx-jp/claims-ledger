---
id: L0062-one-test-answers-confinement-for-configured-paths-and-writes
kind: claim
stated: 2026-09-08T02:13:07-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: c717ee12be35bc06beaf76c9b9ede534fe6dab5fc0f5c6d03fe91102bfb9c831
---

## Assertion

Whether a path leaves the project root is decided by one escape test, used both for the paths a configuration names and for a file the tool is about to write.

## Scope

metric: the number of definitions that decide whether a path escapes the root
cohort: configured paths and write targets
condition: the package as it ships

## Grounds

- code: src/claims_ledger/config.py § "leaves_root" @72ad99b4a138640f009ee09b911c741f84776135
- code: src/claims_ledger/config.py § "confined" @72ad99b4a138640f009ee09b911c741f84776135
- code: src/claims_ledger/config.py § "_escapes" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

confined and leaves_root both reach the same _escapes comparison, over the same symlink-following helper, rather than each carrying a containment test of its own. The two questions are asked at different moments — once when a configuration is read, once when a file is about to be written — and the shape of the failure is identical, so a second implementation would be a second place for the answer to drift.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/config.py · standing · cites-as-live
