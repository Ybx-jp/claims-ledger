---
id: L0085-a-ledger-inside-another-repository-is-unchecked-and-not-clean
kind: claim
stated: 2026-09-08T02:30:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: e5dc5929d83e7d4f868c37db366d6694aa21089b1224a1c663513b50c498d665
---

## Assertion

A ledger with no repository of its own that sits inside somebody else's is reported as a history this run did not check, rather than as one that passed.

## Scope

metric: what a validate run says about immutability when the ledger has no repository recorded
cohort: ledgers nested inside another project's repository
condition: the other checkers already report a check they could not make

## Grounds

- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/schema.py § "enclosing_repository" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

With nothing recorded, check_history asks enclosing_repository whether the entries sit under a repository at all, and reports a failure naming it when they do, together with what to point --root at. Returning an empty list instead is what let validate answer with zero failures over a frozen region a commit was holding — the one checker of the five that said nothing at all about a check it had skipped.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
