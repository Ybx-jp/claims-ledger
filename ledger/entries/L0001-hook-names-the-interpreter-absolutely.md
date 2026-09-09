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

- 2026-09-08T14:43:42-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" @4023af4006273319aec9ae2512d197e4a99fce8c
  artifact: 70593c15b5bc7b0d9c71b393eb5f7f5e1829e29b
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

## References

- README.md · standing · cites-as-live
- src/claims_ledger/cli.py · standing · cites-as-live
