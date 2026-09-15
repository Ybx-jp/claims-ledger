---
id: L0241-a-rewrite-refuses-a-dirty-tree-and-a-branch-another-checkout-holds
kind: claim
stated: 2026-09-14T19:13:43-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 51642fddfbc3f002d81daaf68f5735f0cc5e6da0ca6de165896e6317a8abf270
---

## Assertion

A renumber refuses to write while this checkout has uncommitted changes or while another checkout holds the branch.

## Scope

metric: the outcome of claims-ledger renumber --write in those two states
cohort: every renumber asked to write
condition: the branch resolves and the plan itself was not refused

## Grounds

- code: src/claims_ledger/cli.py § "cmd_renumber" =sha256:2eb26e528fd9a49c9f9b485a87f68b55bd9f53ddc0e763e19459e190210f8fab

## Warrant

cmd_renumber asks checkout_holding and working_tree_changes before it calls rewrite, and both raise rather than write; the command ends by moving a ref and resetting this checkout onto it, and each of those is a way to lose work that was never committed.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
