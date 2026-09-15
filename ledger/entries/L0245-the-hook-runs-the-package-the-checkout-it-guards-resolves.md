---
id: L0245-the-hook-runs-the-package-the-checkout-it-guards-resolves
kind: claim
stated: 2026-09-14T19:35:18-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d119bcdd28769b70b7038de3c87beb1d56f467beb09e541260d3ec13140237d9
---

## Assertion

The installed pre-commit hook runs the interpreter of the checkout it is committing in when that checkout has one this package imports from, and the interpreter recorded at install time otherwise.

## Scope

metric: which interpreter the installed hook runs
cohort: every checkout of a repository the hook is installed in, linked worktrees included
condition: git can name the top level; the candidate is executable and imports the package

## Grounds

- code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" =sha256:9f3f666b4751d909dab1d1dcba787c80eb29d9c7163d84790d98a47c4600f4f7

## Warrant

The template asks git for --show-toplevel and probes that checkout's .venv and venv interpreters with an import of the package, taking the first that answers and leaving the recorded path in place when none does; every checking line then runs whichever it settled on. git answers --git-path hooks with the common directory from every linked worktree, so one hook file serves them all and the interpreter is the only thing that can vary per checkout.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
- docs/OPERATING.md · standing · cites-as-live
