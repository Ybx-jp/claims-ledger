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

- 2026-09-11T19:41:48-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" =sha256:6160c0f534722d9b5eeb02f420943fc33910cec54d0f2e982ad000972b9dcacc
  note: re-read after the commit that gives the two remaining checkers a cached mode. The template now carries the flag on all five lines, which is what this claim requires of it: every line whose checker takes the flag has it, and no other line does. The comment beside it states the one residual left — a ground pinned at working, which resolve reads from the working tree and freshness passes over.

- 2026-09-11T21:12:37-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" =sha256:fc0eb231de2f2314361c4f1c25a188d8f14bbe5feb18335c329b355cb8f6dce7
  note: re-read after the same commit. The template's lines are unchanged — all five still carry the flag, which is what this claim requires — and what moved is the comment beside them, which said a working ground still commits unreported and no longer does.
- 2026-09-14T19:35:33-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" =sha256:fc0eb231de2f2314361c4f1c25a188d8f14bbe5feb18335c329b355cb8f6dce7
  artifact: sha256:d0eeb70717df15bfa85709815f967568186649bdca46bba0cdf3dc567b9b29c6
  note: propagated from a moved ground

- 2026-09-14T19:35:35-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" =sha256:9f3f666b4751d909dab1d1dcba787c80eb29d9c7163d84790d98a47c4600f4f7
  note: re-read after the commit that makes the hook resolve its interpreter from the checkout it is committing in. What this claim asserts is untouched and is now true of two paths rather than one: the recorded path is still sys.executable, an absolute path, and the discovered path is built from git's own --show-toplevel, which is absolute as well. Every checking line still reaches the package with -m and none of them names the console script.

## References

- README.md · standing · cites-as-live
- src/claims_ledger/cli.py · standing · cites-as-live
