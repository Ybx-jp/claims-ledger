---
id: L0186-an-install-that-changed-nothing-exits-zero-and-one-that-skipped-does-not
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 2d00b2abd8bf24aa494e302ff8ec3b9b744c1b02ea406836fe08906e4401e159
---

## Assertion

An install that changed nothing because everything was already in place exits zero, and one that left a file alone does not.

## Scope

metric: the exit code of an install, against what it actually did
cohort: every run of the harness installer
condition: a re-run of the same install, and a run over a file somebody has edited

## Grounds

- code: src/claims_ledger/cli.py § "report_install" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

Three states carry three meanings: something was written, the same bytes were already there, or something else was and was left alone. Running the command twice is not an error, so an install that only found what it would have written exits zero; an install that left a file alone exits non-zero, because the project does not have what it asked for and reporting success would be the one report this tool must never print.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T22:03:38-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "report_install" @52859264d2caa6d447021f4cda3c8b26e7d72c1f
  artifact: 3d06cb1db9f9245227e94c5218c9dd714608ab73
  note: propagated from a moved ground

- 2026-09-08T22:03:53-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "report_install" @fcacc40a38daaecba8fc1084b6dfe2dd34d8631e
  note: re-read after the wiring branch for an agent with nothing to wire was removed. The three states and the exit code each carries are unchanged.
- 2026-09-11T03:10:01-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "report_install" @fcacc40a38daaecba8fc1084b6dfe2dd34d8631e
  artifact: sha256:64b37a1eb40428e9381becfcda564fad17dc94db0ba2aa936780688de42628ea
  note: propagated from a moved ground
- 2026-09-11T03:10:01-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "report_install" =sha256:64b37a1eb40428e9381becfcda564fad17dc94db0ba2aa936780688de42628ea
  note: read against the working tree after report_install began, since the reading at fcacc40, printing an absolute path for a wiring file outside the project and a note that codex reads hooks only there: the three states still map to the same exit codes, zero for wrote and present and non-zero for a file left alone; the assertion holds as written.

## References

- src/claims_ledger/cli.py · standing · cites-as-live
