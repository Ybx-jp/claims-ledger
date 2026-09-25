---
id: L0256-a-checkout-that-would-not-be-listed-is-a-question-not-asked
kind: claim
stated: 2026-09-14T21:13:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6818e0f0542e81b7a58c49de244b010dfc96dc22741fbf0589fabd5b082a1d00
---

## Assertion

A sibling checkout whose entries directory is there and cannot be listed is reported as a question that was not asked, and only a checkout that does not hold the ledger is passed over.

## Scope

metric: what ids_in_the_repository reports when a sibling directory cannot be read
cohort: every checkout git worktree list names
condition: the directory exists; a missing one is a checkout without a ledger and is not a failure

## Grounds

- code: src/claims_ledger/authoring.py § "ids_in_the_repository" =sha256:b922f0946f1de283ffd0e0399bb5cba7e28545659c0bddfd9b19540a3e57af58

## Warrant

The loop separates FileNotFoundError and NotADirectoryError, which mean the checkout carries no ledger, from every other OSError, which means a directory that is there refused to be read; the second appends to the unasked list that create_entry refuses to mint over. Collapsed into one except, an unreadable sibling minted over its entries exactly as if the question were never asked at all.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-24T21:52:04-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "ids_in_the_repository" =sha256:b922f0946f1de283ffd0e0399bb5cba7e28545659c0bddfd9b19540a3e57af58
  artifact: sha256:e8bd12eee15aef4bd16f5323b62282716ca5fd8a675b02a2b3c815fe8b059498
  note: propagated from a moved ground

- 2026-09-24T21:52:23-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "ids_in_the_repository" =sha256:e8bd12eee15aef4bd16f5323b62282716ca5fd8a675b02a2b3c815fe8b059498
  note: re-read after #69. The sibling listing now records which worktree each id was found in; a directory that is there and will not be listed is still reported as unasked, and only a missing one is passed over.

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
