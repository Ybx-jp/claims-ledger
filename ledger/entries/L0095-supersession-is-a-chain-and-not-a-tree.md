---
id: L0095-supersession-is-a-chain-and-not-a-tree
kind: claim
stated: 2026-09-08T02:30:58-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 7cf805c3cc54bab2af075784a233290d993ab2e5f3501c1751aaa8612f04e252
---

## Assertion

Supersession is a chain and not a tree: an entry carries at most one superseded verdict, and its successor's supersedes line names it back.

## Scope

metric: whether a forked or one-sided supersession is reported
cohort: entries carrying a superseded verdict, and entries declaring supersedes
condition: either end of the chain may be the one a reader opens

## Grounds

- code: src/claims_ledger/validate.py § "check_verdicts" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/validate.py § "check_supersession" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_verdicts counts superseded verdicts and fails a second, and requires the verdict to name a successor whose own supersedes line names this entry back. check_supersession comes the other way: a successor whose predecessor carries no superseded verdict fails, and a predecessor already superseded by someone else has the fork reported against the newcomer. Discoverability runs both ways, so a chain broken from either end is caught rather than depending on which entry someone happened to read.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-10T22:05:56-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_verdicts" @34f416118e10a14169475fe23d3176d347d0ed8d
  artifact: sha256:cf64b57b2a6d1b3aad822325eaa3371cbbb7adf635f773ad6e7b53c12cb4341a
  note: propagated from a moved ground
- 2026-09-10T22:06:16-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_verdicts" =sha256:cf64b57b2a6d1b3aad822325eaa3371cbbb7adf635f773ad6e7b53c12cb4341a
  note: read against the working tree after freshness began comparing by digest on both sides: the supersession chain rule is untouched by the artifact-shape edit; the assertion holds as written.
- 2026-09-11T03:57:56-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_verdicts" =sha256:cf64b57b2a6d1b3aad822325eaa3371cbbb7adf635f773ad6e7b53c12cb4341a
  artifact: sha256:2cc50a11f18089b10ca35b6968d534962c348565f1c4911bc74d46621f6af10b
  note: propagated from a moved ground
- 2026-09-11T03:58:17-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_verdicts" =sha256:2cc50a11f18089b10ca35b6968d534962c348565f1c4911bc74d46621f6af10b
  note: read against the working tree after the restatement rule in check_verdicts began exempting a corroboration stated by value, which may name the ground's own digest: one superseded verdict per entry and the successor naming it back are unchanged; the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
