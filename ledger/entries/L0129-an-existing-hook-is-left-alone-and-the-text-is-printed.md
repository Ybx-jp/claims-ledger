---
id: L0129-an-existing-hook-is-left-alone-and-the-text-is-printed
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 2887563e8c3ac713f89152ad9de6cf747a0efa3646338e5ef87f9af314fcd852
---

## Assertion

A pre-commit hook that is already there is left alone and its replacement text is printed instead, including when what is there is a symlink pointing at nothing.

## Scope

metric: what happens when something already occupies the hook path
cohort: hook installation over an existing file or link
condition: a team may share one hook through a symlink

## Grounds

- code: src/claims_ledger/cli.py § "cmd_hook" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

cmd_hook asks whether anything exists at the path without following the link, so a symlink to nothing counts as something someone put there; the ordinary existence test said no to it and the install wrote through it. The question is asked before the containment guard, so a deliberate link to a shared hook is met with the text and an explanation rather than with an accusation about leaving the repository.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
