---
id: L0223-a-cached-run-reads-the-registry-the-commit-will-carry
kind: claim
stated: 2026-09-11T19:50:14-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 4bfce72b4fc91039e991dd1fc32adbf45545e8b1070c8695b5a656e873c6ca57
---

## Assertion

A pointer check asked for the index reads the source registry from the index, so the rows every source ground rests on are the rows the commit will carry.

## Scope

metric: which tree the source registry is read from under the cached flag
cohort: every pointer check given the flag
condition: a registry the index does not hold is read from the working tree, as before

## Grounds

- code: src/claims_ledger/resolve.py § "Sources" =sha256:10b6e2e89ca3151df0f26d542563a1e0be7f6c72ddf21c655f1c4187173c549a
- code: src/claims_ledger/schema.py § "staged_text" =sha256:f99f76b4a11e1dee2180468914794778bbce379ff84fc89bbdd2076dfb5c52d7
- entry: L0035-a-registry-miss-fails-rather-than-passing · distinguishes

## Warrant

The registry is one file, and every source ground in the ledger rests on it, so reading the wrong copy of it is not one pointer answered wrongly but all of them. It was read from the working tree whatever the run was asked. Measured: with an emptied registry staged and the good one restored in the tree, all five checkers report a clean run under the flag, and the state the commit carries fails with every source ground saying the check cannot run. The registry the tree holds was never the subject of that run. This was found by a quality-engineering consultation asked about a different question entirely, and reproduced here before it was repaired. One file is read on its own rather than through the batch the documents go through, because it is one file and the batch exists for the many. The entry named above holds the rule for a registry that has no row for an id; this one is about which registry is asked.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-11T21:12:37-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "staged_text" =sha256:6daf3e9091b8d39dc73fd925bffbd30a2245683b23d55feeefcd512d821bf987
  note: re-read after the same commit, which splits the bytes out into `staged_blob` and leaves this as the decoded convenience over it. The registry is still read from the index under the flag, which is what this ground is cited for.

- 2026-09-11T22:04:31-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "Sources" =sha256:96e0d8199e6c027a3f2c3838f40301b237366c23c0be0d137303dd06c41e583a
  note: re-read after the commit answering the fix-review gate on this branch (qe ticket e9b7d35601214a1b). A registry git could not hand over now stops the run rather than falling back to the working tree's. Which registry is read under the flag is unchanged.

- 2026-09-11T22:04:31-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "staged_text" =sha256:436bb4c123e387d2f441c93598916d631ca5a0f229b933c6c13c628bd03bdab1
  note: re-read after the commit answering the fix-review gate on this branch (qe ticket e9b7d35601214a1b). Split over `staged_blob` and decoded strictly, and a read git did not answer now comes back as a problem. The registry is still read from the index under the flag.

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
- src/claims_ledger/schema.py · standing · cites-as-live
