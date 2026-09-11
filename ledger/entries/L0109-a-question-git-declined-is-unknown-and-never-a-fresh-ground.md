---
id: L0109-a-question-git-declined-is-unknown-and-never-a-fresh-ground
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 026598a5c8f712a32250daf4f1221e9bca1e4261dc9543847b6c34b70277bdc8
---

## Assertion

A question version control declined to answer produces an unknown finding carrying the reason, and is never reported as a fresh ground.

## Scope

metric: the finding when a comparison could not be made
cohort: pinned evidence grounds
condition: the repository-level check passes and an individual command still fails

## Grounds

- code: src/claims_ledger/freshness.py § "drift" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

drift reports unknown, with the reason, for every command it could not get an answer out of: classifying the pin, reading the artifact at the pin, reaching the artifact now, and the comparison itself. The repository-level check asked once before the run cannot see these — asking for the git directory goes on succeeding through a clean filter that exits non-zero, a pack that can no longer be opened, an object removed from under a revision. The comparison did not happen, and a comparison that did not happen is never a fresh ground.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-10T22:05:57-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "drift" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
  artifact: sha256:ec78ecef0788830e1fe16fe77e34d9d23292efbc3622b7af29e1defa9a216ff6
  note: propagated from a moved ground
- 2026-09-10T22:06:17-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "drift" =sha256:ec78ecef0788830e1fe16fe77e34d9d23292efbc3622b7af29e1defa9a216ff6
  note: read against the working tree after freshness began comparing by digest on both sides: a pin git cannot classify, a blob it cannot read at the pin, and a path it cannot compare still come back as unknown with the reason; the assertion holds as written.

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
