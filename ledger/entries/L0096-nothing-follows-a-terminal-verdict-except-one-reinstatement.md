---
id: L0096-nothing-follows-a-terminal-verdict-except-one-reinstatement
kind: claim
stated: 2026-09-08T02:30:58-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 90b663cc145d106dbbe36d498067469dafebdf64df601356f61b49e5afcd69d7
---

## Assertion

Nothing follows a terminal verdict, with one exception: a superseded verdict after a refuted or a non-comparable one, which is how a fallen entry is reinstated by a successor.

## Scope

metric: which verdicts are legal after a terminal one
cohort: entries carrying a terminal verdict
condition: the exception is allowed once

## Grounds

- code: src/claims_ledger/validate.py § "check_verdicts" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_verdicts records the terminal status and fails every verdict after it, permitting a single superseded that follows a refuted or a non-comparable. A terminal verdict closes the entry; letting verdicts follow it would let a status be argued back and forth inside a file that is supposed to be a record. The exception exists because a fallen entry is repaired by writing a successor, and the supersession is how the chain records that — once, and only from those two statuses.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-10T22:05:56-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_verdicts" @34f416118e10a14169475fe23d3176d347d0ed8d
  artifact: sha256:cf64b57b2a6d1b3aad822325eaa3371cbbb7adf635f773ad6e7b53c12cb4341a
  note: propagated from a moved ground
- 2026-09-10T22:06:16-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_verdicts" =sha256:cf64b57b2a6d1b3aad822325eaa3371cbbb7adf635f773ad6e7b53c12cb4341a
  note: read against the working tree after freshness began comparing by digest on both sides: the terminal-verdict rule is untouched by the artifact-shape edit; the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
