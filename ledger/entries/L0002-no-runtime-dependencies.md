---
id: L0002-no-runtime-dependencies
kind: claim
stated: 2026-09-07T13:30:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9cadda332c3bbc11354f696d5bebc021c85517e2916fdd494cd7476934b4504c
---

## Assertion

The package declares no runtime dependencies and a Python floor of 3.11, so its checkers run from a plain interpreter.

## Scope

metric: the dependencies and requires-python fields of the project table
cohort: claims-ledger as declared in pyproject.toml
condition: an installation from the wheel or from the checkout

## Grounds

- toml: pyproject.toml § "project" @4023af4006273319aec9ae2512d197e4a99fce8c

## Warrant

The project table carries an empty dependencies array and requires-python at 3.11, which is the release where tomllib entered the standard library.

## Backing

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-07T21:13:45-07:00 · contested · grade: measured · author: propagation
  evidence: toml: pyproject.toml § "project" @4023af4006273319aec9ae2512d197e4a99fce8c
  artifact: 234538ea4cc75af521d309063aac8535d24e7bcb
  note: propagated from a moved ground

- 2026-09-07T21:14:00-07:00 · superseded · grade: measured · author: main
  evidence: entry: L0011-no-runtime-dependencies · supersedes
  note: the ground was the whole project table; the successor pins the two keys the claim is about

## References

