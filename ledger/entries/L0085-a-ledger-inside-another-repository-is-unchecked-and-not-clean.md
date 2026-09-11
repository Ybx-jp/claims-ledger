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
- 2026-09-08T19:39:25-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "enclosing_repository" @34f416118e10a14169475fe23d3176d347d0ed8d
  artifact: 7f8be52d4717c0dd5907f094259f3cedaca20cb7
  note: propagated from a moved ground

- 2026-09-08T19:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "enclosing_repository" @225f5867b2591ffc5b3020dfe20ca407d81ee06f
  note: read against commit 225f586, which moved `ARCH-AUDIT.md` into `docs/audits/` and rewrote the mentions of it in this section; the section was parsed at the pin and at that commit and compared with comments and docstrings set aside, and the two are identical, so nothing the claim rests on changed
- 2026-09-11T03:10:33-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_history" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  artifact: sha256:a0f5460dc7e6805f42f37f08c07a994eaac5dd9d160914c883daecf28f17db9b
  note: propagated from a moved ground
- 2026-09-11T03:10:33-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_history" =sha256:a0f5460dc7e6805f42f37f08c07a994eaac5dd9d160914c883daecf28f17db9b
  note: read against the working tree after the only edit to check_history since the reading at 2a76453, a comment naming the audit file by its path docs/audits/ARCH-AUDIT.md instead of by its bare name, which sits in the very branch this claim rests on: with no repository recorded, enclosing_repository is still asked and a holder is still reported as a failure naming what to point --root at; the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
