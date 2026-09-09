---
id: L0135-init-and-corpus-open-no-ledger
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 048abb38c26e83347f643914242206a3eeb5159a7e42738938473e2b9b1891d1
---

## Assertion

The scaffolder and the corpus runner are dispatched without opening a ledger, so a configuration that is absent or belongs to another project cannot stop either of them.

## Scope

metric: whether a configuration is required before these two commands run
cohort: the init and corpus subcommands
condition: one creates the configuration and the other brings its own

## Grounds

- code: src/claims_ledger/cli.py § "NO_LEDGER" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395
- code: src/claims_ledger/cli.py § "main" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

NO_LEDGER names the two, and main skips opening a ledger for them. The scaffolder exists precisely because there is no configuration yet, and requiring one would make the command that creates it impossible to run. The corpus builds its own ledgers in temporary repositories, so a configuration found by searching upward from wherever it was invoked is one it must not adopt.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T21:45:08-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "NO_LEDGER" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395
  artifact: 5635a9c60c547010c5878fd5589837af4db0ac77
  note: propagated from a moved ground

- 2026-09-08T21:45:08-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "main" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395
  artifact: 5635a9c60c547010c5878fd5589837af4db0ac77
  note: propagated from a moved ground

- 2026-09-08T21:45:28-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "NO_LEDGER" @52859264d2caa6d447021f4cda3c8b26e7d72c1f
  note: re-read after `harness` joined the set. The scaffolder and the corpus runner are still dispatched without opening a ledger, which is what this entry asserts; a third command doing the same does not touch it. What the installer promises is a claim of its own.

- 2026-09-08T21:45:28-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "main" @52859264d2caa6d447021f4cda3c8b26e7d72c1f
  note: re-read after the docstring named the installer alongside the scaffolder and the corpus runner. The dispatch it describes is unchanged for both of them.

## References

- src/claims_ledger/cli.py · standing · cites-as-live
