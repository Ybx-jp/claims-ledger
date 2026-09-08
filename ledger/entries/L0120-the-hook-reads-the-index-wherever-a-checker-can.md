---
id: L0120-the-hook-reads-the-index-wherever-a-checker-can
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: ab5b6e70c2d6b8d7746e8c1624db402c6bdd9840e17fd9c1c2fb829acbcb6c7d
---

## Assertion

The installed hook asks each checker for the index wherever that checker has a cached mode of its own, so a drift that is staged and then reverted in the working tree cannot commit unreported.

## Scope

metric: which checkers the hook runs against the index rather than the working tree
cohort: the pre-commit hook this command installs
condition: only two of the five checkers accept a cached mode today

## Grounds

- code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

The template runs the entry validator and the freshness checker with the cached flag. Left bare, the freshness line looked past a staged drift at an already-reverted working tree and found nothing wrong, while the validator saw the stale pointer — so a commit went through carrying a ground nobody had compared. The other three have no cached mode yet and read the working tree, which the template says in as many words rather than leaving a reader to infer it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
