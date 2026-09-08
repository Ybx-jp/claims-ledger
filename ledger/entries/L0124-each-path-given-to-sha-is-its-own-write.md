---
id: L0124-each-path-given-to-sha-is-its-own-write
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: e1a2781ea8c2d05d55f2207a834c43c60d1a7fa55015970701b05dde84b62d58
---

## Assertion

Each path given to the fingerprint command is its own write, so a refusal on one does not leave the paths after it unwritten and unnamed.

## Scope

metric: what happens to the remaining paths after one is refused
cohort: invocations naming more than one entry
condition: a refusal is an ordinary outcome, such as an entry already committed

## Grounds

- code: src/claims_ledger/cli.py § "cmd_sha" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

cmd_sha catches the refusal per path, prints it, and carries the worst status forward. Letting the refusal out of the loop left every path after it neither written nor mentioned, which reads as a run that stopped where it says it stopped — and the paths were given in one command precisely because they were meant to be handled together.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
