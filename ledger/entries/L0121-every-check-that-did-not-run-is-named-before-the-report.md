---
id: L0121-every-check-that-did-not-run-is-named-before-the-report
kind: claim
stated: 2026-09-08T02:42:36-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 1cd9ecee29e370700ceb8e85724e452ae04774afa56b5236a03d66d5347fc7ec
---

## Assertion

Every case in which a run checks less than the documentation promises is printed before the report it would otherwise contradict.

## Scope

metric: whether a skipped check is named to the reader
cohort: runs where the repository, the index, or a document could not be read
condition: the report itself would read as a clean one

## Grounds

- code: src/claims_ledger/cli.py § "skipped_checks" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395
- code: src/claims_ledger/cli.py § "guard" @a3df5b5b0d1ea7ec0d3cd95ba40a2aaa3d716395

## Warrant

skipped_checks collects each case — a ledger with no repository of its own, a repository that cannot answer, an unreadable index, a document that could not be opened — and guard prints them before any checker runs. A report of zero failures over a check that never happened is the one output this tool must never produce, and each line here is a place the machinery would otherwise be quietly doing less than it says. The wording is kept weaker than the checker's own where the checker knows more: a ledger with no repository of its own may still sit inside one, and the validator reports that case by name.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/cli.py · standing · cites-as-live
