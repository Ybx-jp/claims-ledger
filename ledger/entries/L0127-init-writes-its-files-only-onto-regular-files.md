---
id: L0127-init-writes-its-files-only-onto-regular-files
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d46fb051739d38f1c0fdb736b958a5838d28eb88b690e024aef83ddfcac02b45
---

## Assertion

The scaffolder writes the configuration and the cache ignore file only onto regular files, and refuses a path holding something else.

## Scope

metric: the outcome of scaffolding onto a FIFO or a directory
cohort: the two files the command may write over
condition: the registry is written only when it is absent

## Grounds

- code: src/claims_ledger/cli.py § "cmd_init" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

cmd_init tests each of those two paths for being something other than a regular file and refuses with the path named. Opening a FIFO for writing blocks until a reader appears, which is a job wedged with no output at all — and a wedged scaffolder in a hook or a script is indistinguishable from one that is slow. The registry is exempt because it is written only when nothing is there.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
