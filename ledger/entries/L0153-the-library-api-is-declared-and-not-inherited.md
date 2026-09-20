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
- 2026-09-11T03:10:01-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/__init__.py § "__all__" @3d35a815b1a4ae4b2da74af69e2c413230f597b5
  artifact: sha256:0ec437883e7b9f8c693d8fae4377e96eeed176283a2060cbc712f87adf8dde74
  note: propagated from a moved ground
- 2026-09-11T03:10:01-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/__init__.py § "__all__" =sha256:0ec437883e7b9f8c693d8fae4377e96eeed176283a2060cbc712f87adf8dde74
  note: read against the working tree after two citing comments were added inside the list since the reading at 3d35a81: the five checkers are still named in the export list beside the vocabulary; the assertion holds as written.
- 2026-09-20T13:22:53-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/__init__.py § "__all__" =sha256:0ec437883e7b9f8c693d8fae4377e96eeed176283a2060cbc712f87adf8dde74
  artifact: sha256:e68f195e3420d000c760257f7a0c0fa4eb15d1ac5e0414dc31274fd5e5a2117e
  note: propagated from a moved ground

- 2026-09-20T13:23:13-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/__init__.py § "__all__" =sha256:e68f195e3420d000c760257f7a0c0fa4eb15d1ac5e0414dc31274fd5e5a2117e
  note: re-read after the commit that converts this file's markers to the short form. The only change inside the section is the citation itself, which lost the entry's slug and now names the id alone; it resolves to the same entry, under the same act, and the References row is unchanged. The list is untouched: the five checkers are still named in it rather than left to implicit submodule import.


## References

- src/claims_ledger/__init__.py · standing · cites-as-live
