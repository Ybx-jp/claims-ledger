---
id: L0216-the-hook-asks-the-index-of-every-checker-that-takes-the-flag
kind: claim
stated: 2026-09-11T15:06:19-07:00
author: main
grade: measured
verbatim_change: assertion drops the consequence clause it inherited, which claimed more than the template decides; Backing unchanged
supersedes: L0212-the-hook-asks-for-the-index-wherever-a-checker-has-a-cached-mode
verbatim_sha: d57095382c7192cacbdf3353aea0ff15a551e0be43c4e8a17a4dc6eb24054e19
---

## Assertion

The installed hook asks each checker for the index wherever that checker has a cached mode of its own, so what those checkers report is what the commit will carry rather than what the working tree held when the commit was made.

## Scope

metric: which checkers the hook runs against the index rather than the working tree
cohort: the pre-commit hook this command installs
condition: whichever checkers have a cached mode of their own are asked for it, and how many that is is read off the template rather than fixed here

## Grounds

- code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" =sha256:d06993cdf185d0d14a901a2219c9e489349385ce8c48b3d25eeb773eb7d2f834

## Warrant

The template runs the entry validator, the pointer resolver and the freshness checker with the cached flag, and the remaining two bare. Left bare, the freshness line looked past a staged drift at an already-reverted working tree and found nothing wrong while the validator saw the stale pointer; and a bare resolve answered for a by-value anchor against the working tree while the commit carried the index. The predecessor went on to say that a drift staged and then reverted cannot commit unreported, and that is more than this template decides: references and propagate have no cached mode and read the working tree, and resolve reads it too for a ground pinned at working, which freshness passes over entirely. So the claim is what the hook asks for, and the residual is stated in the template beside it rather than denied here.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/cli.py · standing · cites-as-live
