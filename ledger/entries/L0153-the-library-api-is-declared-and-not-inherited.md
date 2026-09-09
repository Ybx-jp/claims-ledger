---
id: L0153-the-library-api-is-declared-and-not-inherited
kind: claim
stated: 2026-09-08T02:49:38-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 92b4073b653c913e9a47e8d67391589a4a41078e7b0e17cacad2a9c2636111d8
---

## Assertion

The five checkers are declared exports of the package rather than submodules that happen to be importable.

## Scope

metric: whether the checkers appear in the declared export list
cohort: validate, resolve, references, propagate and freshness
condition: the documentation advertises them as the library interface

## Grounds

- code: src/claims_ledger/__init__.py § "__all__" @94e61e9404b22bd766f6cd97126c73413d0c7e2e

## Warrant

__all__ names the five alongside the rest of the interface. Importing a submodule by name from a package works because the package imported it first, which is an accident of how Python loads modules rather than a promise anyone made — and a refactor that stopped importing one at the top would break a documented interface with nothing to say it had. Declaring them makes the interface the thing that is checked.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T13:17:56-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/__init__.py § "__all__" @94e61e9404b22bd766f6cd97126c73413d0c7e2e
  artifact: d88ddc2f9fa96ab9afc61043b7007ffd0c33a166
  note: propagated from a moved ground

- 2026-09-08T13:35:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/__init__.py § "__all__" @3d35a815b1a4ae4b2da74af69e2c413230f597b5
  note: read against the change in commit 3d35a81, which added ENTRY_ACTS to the export list so the act vocabulary can be printed rather than remembered; the five checkers this claim names are declared exactly as before

## References

- src/claims_ledger/__init__.py · standing · cites-as-live
