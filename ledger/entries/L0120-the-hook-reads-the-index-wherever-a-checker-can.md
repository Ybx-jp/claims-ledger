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

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395
  artifact: 70593c15b5bc7b0d9c71b393eb5f7f5e1829e29b
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed
- 2026-09-11T13:35:32-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  artifact: sha256:ef256aa23cc7413d91429d67ef52e2822809552ecd1778bc9a3597b6eabb3170
  note: propagated from a moved ground

- 2026-09-11T13:37:26-07:00 · superseded · grade: measured · author: main
  evidence: entry: L0212-the-hook-asks-for-the-index-wherever-a-checker-has-a-cached-mode · supersedes
  note: the assertion is carried across unchanged; the condition fixed the count of checkers with a cached mode of their own, and resolve gaining one made three where it said two, so the successor names the rule and leaves the counting to the template

## References

