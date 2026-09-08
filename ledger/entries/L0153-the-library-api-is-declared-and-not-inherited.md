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

## References

- src/claims_ledger/__init__.py · standing · cites-as-live
