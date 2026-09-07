---
id: L0001-hook-names-the-interpreter-absolutely
kind: claim
stated: 2026-09-07T13:30:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 76618c131b2fdee179d8d1e7de192beb1e5f8d6d9bdce5f0ac5eb8f3f41d729a
---

## Assertion

The pre-commit hook that hook --install writes names its interpreter by absolute path and reaches the package with -m rather than by console-script name.

## Scope

metric: text of the installed pre-commit hook
cohort: every hook written by claims-ledger hook --install
condition: the hook template as shipped, with the installing interpreter substituted

## Grounds

- code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" @4023af4006273319aec9ae2512d197e4a99fce8c
- code: src/claims_ledger/cli.py § "hook_text" @4023af4006273319aec9ae2512d197e4a99fce8c

## Warrant

Every checking line of the template begins with the python slot and invokes the package as a module, and hook_text fills that slot with sys.executable, which is an absolute path.

## Backing

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- README.md · standing · cites-as-live
- src/claims_ledger/cli.py · standing · cites-as-live
