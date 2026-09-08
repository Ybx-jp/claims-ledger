---
id: L0119-a-failure-exits-non-zero-and-a-flag-exits-zero
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 299777655ba606e8b0b5230cf7a7235a9ccc729ea3aafd2e261d016bc7085790
---

## Assertion

Every subcommand exits non-zero on a failure and zero on a flag, so a hook can be a list of commands and a flag is a report a person judges rather than a gate.

## Scope

metric: the exit code produced for a run holding failures, flags, or neither
cohort: every subcommand that reports
condition: a run may hold both kinds at once

## Grounds

- code: src/claims_ledger/cli.py § "report_command" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395
- code: src/claims_ledger/schema.py § "exit_code" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

exit_code is the single function turning a list of reports into a status, and report_command is the one path the checkers print through. A flag is a judgement a person has to make — a moved artifact that may or may not matter, a refuted grade against a differently graded entry — and gating on it would train an author to pass a flag rather than read it. A failure is a rule broken, and it stops the commit.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
