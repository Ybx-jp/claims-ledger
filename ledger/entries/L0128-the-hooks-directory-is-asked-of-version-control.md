---
id: L0128-the-hooks-directory-is-asked-of-version-control
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 332733affcc3c3c1794ac2ca7fb9ce980c774eee17666b3d8e31b28ad47345bb
---

## Assertion

The directory the hook is installed into is asked of version control rather than assumed to be the default one.

## Scope

metric: how the hooks directory is determined
cohort: hook installation in any repository
condition: a repository may set a hooks path, be a linked worktree, or keep its data elsewhere

## Grounds

- code: src/claims_ledger/cli.py § "hooks_dir" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

hooks_dir asks rev-parse for the hooks path, which is the question git asks itself, and resolves the answer against the repository. Guessing the default directory is wrong three ways this package cannot afford: a configured hooks path makes the install a file git will never execute, and in a linked worktree or with a separated git directory the guess is not even a directory. A hook installed where git does not look is a gate that does not exist, announced as installed.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
