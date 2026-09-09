---
id: L0194-git-is-asked-in-one-language-and-told-not-to-trace
kind: claim
stated: 2026-09-09T10:18:04-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6841a223f49617c5e683f569bbefe8785bb69d8f3afbd3c067810b1248ec8e89
---

## Assertion

Every git call is made in the C locale and with the tracing variables dropped, so what a command prints is decided by the repository it was asked about and not by the environment it was asked from.

## Scope

metric: what decides the text a git command prints, beyond the repository itself
cohort: every git call this package makes
condition: the call is being built; nothing is asked of a command already running

## Grounds

- code: src/claims_ledger/schema.py § "git_env" @b73beb89121b47f1e945220810dfaae2c9ac4844

## Warrant

Everything this package learns from version control it learns by parsing what a command printed — the commits a walk listed, the paths under them, the bytes of a blob — and a locale decides what some of that printing looks like. Pinning it is what makes the same repository answer the same way on two machines, and it costs nothing, because nothing here wants the operator's language. The tracing variables are the same question from the other side: each makes a command write diagnostics onto the streams this package reads, so an operator who exported one while debugging something else would have it arrive as though the command had said it. Both are decided where the environment for a call is built, beside the variables that would send the call at the wrong repository, rather than guarded against separately by each reader.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
