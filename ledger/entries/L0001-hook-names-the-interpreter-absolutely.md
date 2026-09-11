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
- 2026-09-11T13:35:32-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  artifact: sha256:ef256aa23cc7413d91429d67ef52e2822809552ecd1778bc9a3597b6eabb3170
  note: propagated from a moved ground

- 2026-09-11T13:36:03-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" =sha256:ef256aa23cc7413d91429d67ef52e2822809552ecd1778bc9a3597b6eabb3170
  note: read against the commit that points the hook's resolve line at the index. This claim is about how the interpreter is named, not about which flags the checking lines carry: every checking line still begins with the python slot and reaches the package with -m, and hook_text still fills that slot with sys.executable.

- 2026-09-11T13:38:35-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" =sha256:942ba9cbee29435b9afade468b70c036de4abd07b6e7e016882f1ff9faa7fbf5
  note: re-read after the citing comment below the template moved from L0120 to its successor L0212, which is inside this section and so changed its digest again in the same commit. The template itself is untouched by that move and the claim is unaffected.

- 2026-09-11T15:07:33-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" =sha256:d06993cdf185d0d14a901a2219c9e489349385ce8c48b3d25eeb773eb7d2f834
  note: re-read after the sentence below the template was corrected and its citation moved to L0216. The template's own lines are untouched: each still begins with the python slot and reaches the package with -m.

- 2026-09-11T16:07:05-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" =sha256:64ff75703d6e7dc76ef58f6a949f2a473b9a5898b0f825c3d801f012c5e64407
  note: re-read after the template's comment gained the resolver's working-pin residual and the sentence below it was cut back to what the template settles. The checking lines themselves are untouched: each still begins with the python slot and reaches the package with -m.

## References

- README.md · standing · cites-as-live
- src/claims_ledger/cli.py · standing · cites-as-live
