---
id: L0257-a-rewrite-is-refused-where-the-commits-would-lose-their-signatures
kind: claim
stated: 2026-09-14T21:13:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 5c1b6ca9704e0790f80b759b974dcb0a233a5fd91d67f3cfcd4cc708a6c1f6d1
---

## Assertion

A rewrite is refused in a repository that signs its commits, rather than writing unsigned ones.

## Scope

metric: the refusals a renumber reports in a repository configured to sign
cohort: every renumber in a repository with commit.gpgsign set
condition: the setting is read from git config as one of git's true values

## Grounds

- code: src/claims_ledger/renumber.py § "refusals" =sha256:6c7b6808a17b8f2d175b6b889b17e1ca965f91ed3b8873562d27b8287b964781

## Warrant

refusals asks git config for commit.gpgsign and reports a refusal when it is set, because rewrite builds each commit with commit-tree, which does not sign: measured on git 2.43.0, under commit.gpgsign=true and a gpg.program that cannot run, commit-tree wrote an unsigned commit at exit 0 and said nothing. No second rewrite is available to repair the result.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
