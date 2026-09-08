---
id: L0011-no-runtime-dependencies
kind: claim
stated: 2026-09-07T21:14:00-07:00
author: main
grade: measured
supersedes: L0002-no-runtime-dependencies
verbatim_sha: 9cadda332c3bbc11354f696d5bebc021c85517e2916fdd494cd7476934b4504c
---

## Assertion

The package declares no runtime dependencies and a Python floor of 3.11, so its checkers run from a plain interpreter.

## Scope

metric: the dependencies and requires-python fields of the project table
cohort: claims-ledger as declared in pyproject.toml
condition: an installation from the wheel or from the checkout

## Grounds

- toml-key: pyproject.toml § "dependencies" @d1474db8b09e734b7a1c975e1b24aa6107438af1
- toml-key: pyproject.toml § "requires-python" @d1474db8b09e734b7a1c975e1b24aa6107438af1

## Warrant

The dependencies key carries an empty array and requires-python names 3.11, which is the release where tomllib entered the standard library. Each is pinned as itself rather than as the table holding it, so the claim goes stale when one of those two settings changes and not when a classifier is added beside them.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T15:43:45-07:00 · contested · grade: measured · author: propagation
  evidence: toml-key: pyproject.toml § "dependencies" @d1474db8b09e734b7a1c975e1b24aa6107438af1
  artifact: 8c26797e65fb0ea7aa79b643eaa5b832b4bf7a38
  note: propagated from a moved ground

- 2026-09-08T16:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: toml-key: pyproject.toml § "dependencies" @abb827e3cd4a443f4cc9e90f1db52a3d5c853622
  note: read against commit abb827e, which moved this claim's citing comment below the key rather than above it, where a toml-key section does not reach; the key is still an empty array and requires-python still names 3.11

## References

- README.md · standing · cites-as-live
- pyproject.toml · standing · cites-as-live
- src/claims_ledger/schema.py · standing · cites-as-live
