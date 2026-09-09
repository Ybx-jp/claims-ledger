---
id: L0114-pinned-grounds-without-a-repository-are-a-failure-and-not-silence
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d6f976844f9225ba666b56748e87baae5de9f04488af5cf2f22badf277af2f41
---

## Assertion

A ledger holding grounds pinned to commits, with no repository to ask about them, is a failure naming how many grounds went unchecked.

## Scope

metric: what a run reports when there are pinned grounds and no repository
cohort: ledgers outside version control, or whose repository is unreadable
condition: the ledger holds at least one pinned evidence ground

## Grounds

- code: src/claims_ledger/freshness.py § "run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

run counts the pinned grounds and, finding no repository, returns a single failure saying that freshness did not run over them; a repository that cannot answer at all is reported the same way. Silence here would be the failure mode this package exists to refuse — a check that did not run, reported as a check that passed — and it would be silence over exactly the grounds the checker was written for.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
  artifact: 7bf8ce83b6bb554674722efe7e644aa962b022ef
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
