---
id: L0240-a-rewrite-builds-every-commit-before-it-moves-the-branch
kind: claim
stated: 2026-09-14T19:13:42-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: ab188d5a8c5ad3d8fedad56f1b121e1c0e900b48a21e526a22a21eadf3f9c5c0
---

## Assertion

A renumber writes every rewritten commit before it moves any ref, so a rewrite that fails part way leaves the branch where it was.

## Scope

metric: the state of the branch after a failed rewrite
cohort: every renumber that does not run to completion
condition: the failure is anything the rewrite reports as a RenumberError

## Grounds

- code: src/claims_ledger/renumber.py § "rewrite" =sha256:a7617476abb94765a512621eceb0ed9dddeeb4729901b20487f9d02f777c9506

## Warrant

rewrite returns the new tip and moves nothing; the ref is moved afterwards by move_branch, so commits written before a failure are unreferenced objects rather than a branch half rewritten.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-14T20:21:10-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/renumber.py § "rewrite" =sha256:a7617476abb94765a512621eceb0ed9dddeeb4729901b20487f9d02f777c9506
  artifact: sha256:127c4df381a2225c36ff4f40bb433ec9d6913eff56dccff33ee216a6bce3dcd9
  note: propagated from a moved ground

- 2026-09-14T20:21:11-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/renumber.py § "rewrite" =sha256:127c4df381a2225c36ff4f40bb433ec9d6913eff56dccff33ee216a6bce3dcd9
  note: re-read after the commit that fixes what the pre-merge gate found. The section still returns the new tip and moves nothing; move_branch is still the only caller that touches a ref, so a rewrite that fails part way still leaves unreferenced objects and a branch where it was.
- 2026-09-14T21:05:00-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/renumber.py § "rewrite" =sha256:127c4df381a2225c36ff4f40bb433ec9d6913eff56dccff33ee216a6bce3dcd9
  artifact: sha256:6cd425bf812e4e09ddcf364613942acceb419796dd3905cb185315335de957e1
  note: propagated from a moved ground

- 2026-09-14T21:05:02-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/renumber.py § "rewrite" =sha256:6cd425bf812e4e09ddcf364613942acceb419796dd3905cb185315335de957e1
  note: re-read after the commit that answers the gate's second round. The section still returns the new tip and still moves nothing; move_branch remains the only caller that touches a ref.

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
