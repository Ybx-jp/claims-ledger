---
id: L0094-a-corroborating-verdict-points-somewhere-new
kind: claim
stated: 2026-09-08T02:30:58-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 7ce9ac765b9df30d3709213a6b9753638a7b2450ce89c30811e66cbda9bb43a5
---

## Assertion

A corroborating verdict is refused when its evidence names a ground the entry already cites.

## Scope

metric: whether a corroborating verdict restating an existing ground is reported
cohort: verdicts with status corroborated
condition: the comparison is on the normalized pointer text

## Grounds

- code: src/claims_ledger/validate.py § "check_verdicts" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_verdicts normalizes the entry's grounds and the verdict's evidence and fails on a match. A corroboration asserts that somebody went and looked; pointing at the ground the entry already rests on records no looking at all. This is what makes the verdict the record of a reading rather than a restatement, and it is the discharge the repair procedure depends on when an artifact has moved and the claim has not.

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
  note: read against the working tree after freshness began comparing by digest on both sides: the corroboration rule is untouched by the artifact-shape edit; the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
