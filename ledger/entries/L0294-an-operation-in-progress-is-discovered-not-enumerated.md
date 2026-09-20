---
id: L0294-an-operation-in-progress-is-discovered-not-enumerated
kind: claim
stated: 2026-09-20T15:23:32-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 380b30963b77868332ac76689fa2be427158f43c146446dc7302b3cd7756c59f
---

## Assertion

The other side of an operation in progress is found by listing the git directory, and while one is in progress a file no walk named is reported as a question that could not be settled rather than as a file no commit holds.

## Scope

metric: what is reported for a file no walk named while an operation is in progress
cohort: the question whether git already holds a file
condition: a merge, cherry-pick, revert or rebase is in progress, or nothing is

## Grounds

- code: src/claims_ledger/schema.py § "operation_heads" =sha256:a8fdefec5546c7bd2a105353453e8cb265a5d28f628396547a4db3771921905f
- code: src/claims_ledger/schema.py § "OPERATION_HEADS_IGNORED" =sha256:4b869202be2f010f4f09883b68a3b4c482a5da542b87aa6ea432a53fbaa53f0b
- code: src/claims_ledger/authoring.py § "is_committed" =sha256:fd9312e13d08a2331bf9b6f92ef38c0968083bbc03d702926ff16ccc9b045807

## Warrant

Pseudo-refs are discoverable and not enumerable: git grows operations, and a list of names written into this package answers no operation in progress for the first one it has not been taught. That answer is the destructive direction, because a file read as uncommitted is a file whose frozen region may be rewritten. So the directory is listed rather than a list consulted, and the negative is downgraded a second time: inside any operation, not named by the walk becomes could not be established, which both callers already refuse on. ORIG_HEAD and FETCH_HEAD are left out — the first is where the operation started and the second is a list rather than one commit, and neither is a side of the commit being made.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- src/claims_ledger/authoring.py · standing · cites-as-live
