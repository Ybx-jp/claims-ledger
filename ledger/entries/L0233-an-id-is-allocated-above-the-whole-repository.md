---
id: L0233-an-id-is-allocated-above-the-whole-repository
kind: claim
stated: 2026-09-14T19:01:40-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 4a7809f5ade5aadcaae50e53967ed9c8760dad02344f5384612b2f9379f02a52
---

## Assertion

An entry id is allocated above every id the repository holds — the entries of this checkout, every entry filename any ref has carried, and the entries each sibling worktree holds including the ones it has not committed — rather than above the entries of one checkout.

## Scope

metric: the id claims-ledger new allocates
cohort: every mint in a repository holding more than one checkout or branch
condition: git can be asked; a mint that names its own id with --ident allocates nothing

## Grounds

- code: src/claims_ledger/authoring.py § "ids_in_the_repository" =sha256:8f792e8cf50870fdc28b910ff923b5181c54f7913211485b6a5cdddc5e344eaf
- code: src/claims_ledger/authoring.py § "next_id" =sha256:a5266e51a2e0e6ce6f5624e3b64305245f428ba2642437e8e7efdf8e5112e577

## Warrant

ids_in_the_repository reads every entry filename added under the entries directory on any ref, in one walk, and lists the entries directory of each checkout git worktree list names; next_id folds that set into the numbers already in use before it takes the highest and adds one, so a number held anywhere in the repository is not allocated a second time.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-14T21:14:18-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "ids_in_the_repository" =sha256:8f792e8cf50870fdc28b910ff923b5181c54f7913211485b6a5cdddc5e344eaf
  artifact: sha256:b922f0946f1de283ffd0e0399bb5cba7e28545659c0bddfd9b19540a3e57af58
  note: propagated from a moved ground

- 2026-09-14T21:14:19-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "ids_in_the_repository" =sha256:b922f0946f1de283ffd0e0399bb5cba7e28545659c0bddfd9b19540a3e57af58
  note: re-read after the commit that answers the gate's remaining findings. The section gained `-m` on the walk and a separated OSError. Both make this claim more nearly true rather than less: the walk now also sees an entry created by a merge commit, which git prints no diff for otherwise, and a sibling directory that refuses to be read is reported instead of passed over. What the claim asserts about where ids are looked for — this checkout, every ref, every sibling worktree — is unchanged.

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
- src/claims_ledger/renumber.py · standing · cites-as-live
- docs/OPERATING.md · standing · cites-as-live
