---
id: L0012-a-propagated-append-is-still-a-failing-run
kind: claim
stated: 2026-09-07T22:47:38-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 244f3a7056ff96baf2a5582afcf800eb7c0159639f5d5f7c6b4890f8485d60b9
---

## Assertion

A verdict propagation owes an entry is reported as a failure whether or not `--write` appended it, so the run that repairs the ledger is itself a failing run.

## Scope

metric: the reports propagate returns for a propagated verdict that is missing
cohort: every dependent owed a contested verdict by the propagation author, whether from a live-cited ground that fell or from a challenges act against it
condition: the same ledger run with --write and without it

## Grounds

- code: src/claims_ledger/propagate.py § "run" @e80ad36e50c2c2a2afab6603592ff5fb1818f89e

## Warrant

run appends the fail Report in the same branch that queues the verdict block, before write is consulted at all, and the write branch only adds flag Reports on top of the reports already collected; no path through run turns an appended verdict into a report list without its failure in it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T09:41:22-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/propagate.py § "run" @e80ad36e50c2c2a2afab6603592ff5fb1818f89e
  artifact: d7edcf2d43d01f126a1240c49607dcd4d379e414
  note: propagated from a moved ground

- 2026-09-08T09:50:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/propagate.py § "run" @5ee55ae6992f10c834510759f026644f42614025
  note: read against the change in commit 5ee55ae, which narrowed the dependent exemption from FALLEN to TERMINAL in that one branch; this claim names a different part of the same section and is unaffected

## References

- src/claims_ledger/propagate.py · standing · cites-as-live
