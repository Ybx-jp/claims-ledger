---
id: L0022-nothing-is-written-through-a-link-that-leaves-the-root
kind: claim
stated: 2026-09-07T23:17:46-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 058edeaa707065a5209aa7b9d2bb822243572f94a4cc82cb8bcab474e503e32b
---

## Assertion

A verdict is not appended through an entry path that resolves outside the project root, even when that entry sits inside the configured entries directory.

## Scope

metric: whether an append proceeds for an entry whose path leaves the root
cohort: entry files reached through a symlink out of the entries directory
condition: the entries directory itself is confined, and the individual file is not

## Grounds

- code: src/claims_ledger/propagate.py § "append_verdict" @0af113005f955a4e120d71338993a94cc6efeb7b

## Warrant

append_verdict asks leaves_root about the entry's path before it reads or writes anything and raises with the escaping destination named. Confining the entries directory does not settle the files in it: an entry inside it can be a symlink to anywhere, which is the second way out and the one this guard closes.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
