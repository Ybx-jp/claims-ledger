---
id: L0004-configured-paths-stay-under-the-root
kind: claim
stated: 2026-09-07T13:30:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 1e9d7db676a3a5d7644e1104d0d0b272a14bbf1cc5ac6e79f55283b2a7863a65
---

## Assertion

Every path a configuration names is refused when it leaves the project root, whether through an absolute value, a parent walk or a symlink, and a documents glob is refused when it addresses outside the root.

## Scope

metric: whether a configured path or glob is honoured
cohort: the ledger, entries, registry, cache and documents settings
condition: a value that resolves outside the root as written or with its links followed

## Grounds

- code: src/claims_ledger/config.py § "confined" @4023af4006273319aec9ae2512d197e4a99fce8c
- code: src/claims_ledger/config.py § "confined_pattern" @4023af4006273319aec9ae2512d197e4a99fce8c

## Warrant

confined tests the joined path as written and again with symlinks followed and raises ConfigError on either escape; confined_pattern applies the lexical test to a documents glob.

## Backing

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- README.md · standing · cites-as-live
- src/claims_ledger/config.py · standing · cites-as-live
