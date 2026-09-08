---
id: L0130-the-hook-is-not-installed-through-an-escaping-link
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: c1b965026bf51ea3271e397e1e89c46e61e164aef3291a0255005014d7c68625
---

## Assertion

The hook is not written through a link that leaves the hooks directory, including when the hooks directory is itself the link.

## Scope

metric: whether the hook write is confined to the hooks directory
cohort: hook installation where nothing occupies the hook path
condition: the link may be at the hook name or one level up

## Grounds

- code: src/claims_ledger/cli.py § "cmd_hook" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

With nothing at the path, cmd_hook asks where the write would land relative to the hooks directory and refuses an answer outside it. A dangling link at the hook name took an executable shell script outside the project at exit 0, naming the in-root path it had not written to; a link at the hooks directory does the same one level up, and the existence test cannot see that one at all. Refusing is the only safe answer, because the file being written is executed by git.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
