---
id: L0181-an-installed-hook-script-is-executable
kind: claim
stated: 2026-09-08T21:44:39-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 7b6fdeed3a21fe7d52dbb0b2ba35dd771dfd13bb6cb79c5ee81177d8cce1ab69
---

## Assertion

A hook script is written with an executable mode rather than with whatever mode the packaged file happens to carry.

## Scope

metric: the mode an installed hook script is written with
cohort: every hook script the installer writes
condition: the package may have been installed from a wheel, which is a zip

## Grounds

- code: src/claims_ledger/harness.py § "plan" @52859264d2caa6d447021f4cda3c8b26e7d72c1f

## Warrant

The plan names mode 755 for every script it carries, rather than copying the mode off the packaged file. A wheel is a zip and an installer need not take an executable bit out of one, so a hook written with the mode the archive happened to preserve is a hook the agent silently never runs: a guard that does not exist, reported as installed.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T22:03:38-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/harness.py § "plan" @52859264d2caa6d447021f4cda3c8b26e7d72c1f
  artifact: 4d3633e3f1e5dcb5b1a3cc27880ee7e3d699a61e
  note: propagated from a moved ground

- 2026-09-08T22:03:53-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/harness.py § "plan" @fcacc40a38daaecba8fc1084b6dfe2dd34d8631e
  note: re-read after the plan stopped reframing a skill's frontmatter per agent. The mode the scripts are written with is unchanged and still named in the plan rather than taken off the packaged file.

## References

- src/claims_ledger/harness.py · standing · cites-as-live
