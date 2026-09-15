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

- 2026-09-14T19:22:21-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "cmd_renumber" =sha256:635481e3694e064746e0075e2e2711ffdb752ade52dd0d85b127cdd775b7852e
  note: re-read after the commit that adds `--on-merge` and the exit-code contract. Both guards this claim is about are untouched and still run before anything is written: checkout_holding is still asked first and working_tree_changes second, and each still raises rather than writing. What moved around them is which paths reach the write at all.
- 2026-09-14T20:21:10-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "cmd_renumber" =sha256:635481e3694e064746e0075e2e2711ffdb752ade52dd0d85b127cdd775b7852e
  artifact: sha256:f20c3f47342e895f7954d6cf9f1e4c0827e057c7bbf481c0b93d40e71ef55ddc
  note: propagated from a moved ground

- 2026-09-14T20:21:11-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "cmd_renumber" =sha256:ec5f0e891c15fe6919ab2825976b488dc830b60974ef6cf38b6f859435750916
  note: re-read after the commit that fixes what the pre-merge gate found. Both guards this claim is about are untouched and still run before anything is written; branch_ref now runs beside them, which is a third refusal on the same path rather than a change to those two.

## References

- src/claims_ledger/cli.py · standing · cites-as-live
