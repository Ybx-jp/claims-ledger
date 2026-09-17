---
id: L0275-a-scratch-directory-that-will-not-be-removed-does-not-fail-the-run
kind: claim
stated: 2026-09-17T00:52:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0cc9fe1ce7139d17ab2766632343993b4fe42cbab02ee31fbc575aa10df0831a
---

## Assertion

A temporary directory the corpus runner cannot remove does not fail the run and is not reported as a defect in the package.

## Scope

metric: what a corpus run reports when the directory a seed was built in cannot be removed
cohort: the scratch directory of one seed, and the run around it
condition: a real git repository inside it, and any writer git starts on its own schedule

## Grounds

- code: src/claims_ledger/corpus/run.py § "scratch" =sha256:6ac3a439bd5c9a1e7e5cf6701f559b018ab17bdd26c006bb3de78c35fcb692d5

## Warrant

A seed's repository is a real one and git writes into `.git` when it decides to, so the tree can gain a file between the walk that lists it and the `rmdir` that follows; Python raises `OSError: [Errno 39] Directory not empty` out of the context manager's exit, where no caller expects it and the CLI's catch-all prints it as a bug report about the package. Measured: run 35194363883 attempt 1, ubuntu-latest 3.14, `claims-ledger: unexpected OSError: [Errno 39] Directory not empty: '/tmp/corpus-hbiy3dvr/.git'`, exit 2, after 71 seeds had passed and none had failed; the re-run of the same commit was green. What the corpus is evidence about is the checkers, and a directory that outlived its deletion says nothing about them, so the removal is allowed to fail while the verdict stands. `gc.auto=0` on every git command the runner makes keeps the writer from starting at all, which is the half that prevents rather than tolerates.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-17T01:12:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/corpus/run.py § "scratch" =sha256:4551a66cb8690bb1c7c13e0105051d8a3b52ec25cd823ed4024f3dc45db5af5d
  note: re-read, and the Warrant's last sentence is corrected here rather than in the frozen region it sits in. Measured on git 2.43.0 under GIT_TRACE and strace: `git -c gc.auto=0 commit` still spawns `git maintenance run --auto`, a distinct child that opens `.git/objects/maintenance.lock` with the flag in force; `git -c gc.auto=0 -c maintenance.auto=false commit` spawns none and the commit still lands. So it is `maintenance.auto=false` that keeps the writer from starting, and `gc.auto=0` that disarms the gc task inside a run which does start and the background fork `gc.autoDetach` would make. Both flags are now on every git command the runner makes. What the entry asserts is unchanged and is what `ignore_cleanup_errors` holds up on its own; the misattribution was in the half that prevents, and nothing rests on it.

## References
