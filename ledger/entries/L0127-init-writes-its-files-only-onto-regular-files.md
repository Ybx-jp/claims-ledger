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

- 2026-09-20T11:38:45-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "cmd_init" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395
  artifact: sha256:495e4593ec7e2f4039b52648b71a0f3cb9c39669dcfd9b9e0b35ce122596e5a3
  note: propagated from a moved ground

- 2026-09-20T11:38:47-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "cmd_init" =sha256:495e4593ec7e2f4039b52648b71a0f3cb9c39669dcfd9b9e0b35ce122596e5a3
  note: cmd_init passes the `code` recipe into the config template as a value instead of carrying it inside the template text; what init writes onto which files, and the containment question it asks of each name, are untouched

## References

- src/claims_ledger/cli.py · standing · cites-as-live
