---
id: L0188-no-symlink-in-the-repository-reaches-into-the-package
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: e06dce269578b2c1388f55ce4173eec48e828af0ca958625706c1fcbb608f01d
---

## Assertion

No symbolic link in this repository points into the package directory, and a test searches the whole tree for one.

## Scope

metric: whether any link in the tree resolves inside src/claims_ledger
cohort: every symbolic link in the working tree, outside version control's own directory and the scratch worktrees
condition: the build follows a link and attributes the file it finds to the path it was reached by

## Grounds

- code: tests/test_harness.py § "test_no_symlink_in_the_repository_reaches_into_the_package" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

An absence is only worth as much as the search behind it, so the search is the ground: the test walks the tree, resolves every link and fails on one that lands in the package. The shortcut it forbids is the one that was there — the three skills were symlinked out of the agent directory into the package, and the build counted each file as seen at a path no distribution includes and dropped the real one, with no error anywhere.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- CLAUDE.md · standing · cites-as-live
