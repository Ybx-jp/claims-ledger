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

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d
  artifact: 3ebabaa4d367b5f9fa08dd065da0555734c20f01
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_history" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

## References

- src/claims_ledger/validate.py · standing · cites-as-live
