---
id: L0118-each-pointer-is-evaluated-once-per-run
kind: claim
stated: 2026-09-08T02:37:35-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 362bd3bdbcd3be4092e2a27d54bf39586cc044bda28d109537d248d975644444
---

## Assertion

Each pointer is evaluated once for the whole run, keyed on the whole pointer rather than on the path it names.

## Scope

metric: the number of times one pointer's finding is computed in a run
cohort: pinned evidence grounds, including several on one artifact
condition: two grounds may name one file and two different sections

## Grounds

- code: src/claims_ledger/freshness.py § "run" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

run memoizes the finding under the pointer as written, which is the identity the orphan rule already looks a ground up by. Keying on the path instead passes the suite and the corpus and silently loses a finding: an entry carrying two grounds on one file naming two sections has the second one's drift answered with the first one's. Every caller runs before the first write, so a verdict appended mid-run cannot change an answer already given, and an edit landing between two evaluations can no longer produce two answers to one question inside one report.

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
