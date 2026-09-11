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
- 2026-09-09T13:28:16-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "run" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  artifact: d3839ddf380073c420e1b127e402cf5d058cad26
  note: propagated from a moved ground
- 2026-09-09T13:28:16-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" @825902da5293a5d7121cfa0a7b9cc6d3d4eb5ef0
  note: read against commit 825902d, which compares each ground from the pointer effective_pointer returns and names that reading in the flag; how a verdict is appended, what a missing repository or an unstatable artifact or a terminal entry gets, and the once-per-run memo are unchanged; the assertion holds as written.
- 2026-09-09T14:03:34-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "run" @825902da5293a5d7121cfa0a7b9cc6d3d4eb5ef0
  artifact: f66a2097acc62a3f20e2c68d4e597975ee945f95
  note: propagated from a moved ground
- 2026-09-09T14:03:35-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" @54aa2e467954028f16a77e1a3d15d9d4b37a40ff
  note: read against commit 54aa2e4, which passes the run's ancestry memo to effective_pointer and orphans; nothing else in the loop changed, and the appends, the failure without a repository, the exit after a write, the unstatable artifact, the terminal exemption and the once-per-run memo hold; the assertion holds as written.
- 2026-09-10T22:05:57-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "run" @54aa2e467954028f16a77e1a3d15d9d4b37a40ff
  artifact: sha256:e95965ef764409d49cfc0a68bcbf017e722714e5427d9bb10082f5f6110e1793
  note: propagated from a moved ground
- 2026-09-10T22:06:18-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "run" =sha256:e95965ef764409d49cfc0a68bcbf017e722714e5427d9bb10082f5f6110e1793
  note: read against the working tree after freshness began comparing by digest on both sides: the memo is still keyed on the whole pointer text; the assertion holds as written.

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
