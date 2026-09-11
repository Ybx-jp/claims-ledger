---
id: L0093-a-propagated-verdicts-artifact-is-checked-in-every-state
kind: claim
stated: 2026-09-08T02:30:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 208e891597f1479ab773f5c822b4b8969a1cd92190590c9908479aeba86a831d
---

## Assertion

The artifact line of a propagated verdict over a pinned ground is checked for shape on every verdict and in every state, before git is asked anything.

## Scope

metric: when and how often a propagated verdict's artifact line is checked
cohort: contested verdicts by the propagation author naming a pinned evidence ground
condition: the drift the verdict records may still be live

## Grounds

- code: src/claims_ledger/validate.py § "check_verdicts" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/schema.py § "OBJECT_ID_RE" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/schema.py § "NULL_OBJECT_ID" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_verdicts requires the line, requires its value to be a forty-character object id or the absent marker, and refuses git's null object id, which is well-formed and names nothing that ever hashed to it. The other checker that reads the value asks only once the ground looks fresh again, so in the state a discharge normally lives in — the drift still live — nothing read it at all: a verdict carrying forty zeros, a value that is not a hash, or a missing line silenced a real ongoing drift with every checker at exit 0.

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
  note: read against the working tree after freshness began comparing by digest on both sides: the artifact line is still checked for shape on every verdict in every state before git is asked; the shapes are now a section digest, the 40-character object id verdicts recorded before anchors could be stated by value, or absent, so the cohort of well-formed values is wider and the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
