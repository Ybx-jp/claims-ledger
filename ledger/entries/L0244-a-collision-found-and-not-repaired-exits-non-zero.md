---
id: L0244-a-collision-found-and-not-repaired-exits-non-zero
kind: claim
stated: 2026-09-14T19:20:55-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 79be63b0918bc226bec4405b482ebe06f70dcddc1b56447e6cb8c171ac6a0063
---

## Assertion

A renumber that finds a collision and does not repair it exits non-zero, and one that finds nothing to move exits zero.

## Scope

metric: the exit code of claims-ledger renumber
cohort: every run of the command
condition: the plan could be made; a branch that cannot be planned is a separate refusal

## Grounds

- code: src/claims_ledger/cli.py § "cmd_renumber" =sha256:635481e3694e064746e0075e2e2711ffdb752ade52dd0d85b127cdd775b7852e

## Warrant

cmd_renumber returns 0 only when the plan is empty or the rewrite was carried out, returns 1 for a collision it was not asked to repair and for one the configured policy refuses, and returns 2 for a refusal or an error; a guard asking the question reads the code rather than the prose.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
