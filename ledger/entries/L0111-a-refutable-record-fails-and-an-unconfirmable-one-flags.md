---
id: L0111-a-refutable-record-fails-and-an-unconfirmable-one-flags
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 4b2b83de08a3a6a11a40a81abfd9661842a409f4308a27f2b93a2945750ebf8f
---

## Assertion

A propagated verdict whose record version control can refute fails, and one it can only fail to confirm flags.

## Scope

metric: the outcome for each of the two ways a recorded artifact is not confirmed
cohort: propagated verdicts over a ground that now reads fresh
condition: an ordinary drift may be recorded and then abandoned before it is committed

## Grounds

- code: src/claims_ledger/freshness.py § "orphans" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
- code: src/claims_ledger/freshness.py § "caused" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

caused separates the two and orphans gives them different outcomes. A record version control can refute — the pin's own blob, which states no drift, or a marker of absence over a history holding no deletion — is the pre-emptive forgery the rule was written for, and it fails. A record it can only fail to confirm is what an ordinary drift looks like when it is never committed: the run records the working-tree blob, the ledger is committed, and the edit is abandoned. Failing that left a permanent red no legal edit could clear, since verdicts append and only append, the pin is frozen, and nothing is appended for a ground that is fresh. The flag does not soften the forgery rule, because a verdict nothing can confirm cannot silence a drift either.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-09T13:28:16-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "orphans" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
  artifact: d3839ddf380073c420e1b127e402cf5d058cad26
  note: propagated from a moved ground
- 2026-09-09T13:28:16-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "orphans" @825902da5293a5d7121cfa0a7b9cc6d3d4eb5ef0
  note: read against commit 825902d, which registers a propagated verdict's cause under the pin and under every reading since, so a reading a later one replaced still names the drift recorded against it; the rule is still asked of the ground, and its two outcomes are unchanged; the assertion holds as written.
- 2026-09-09T14:03:34-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "orphans" @825902da5293a5d7121cfa0a7b9cc6d3d4eb5ef0
  artifact: f66a2097acc62a3f20e2c68d4e597975ee945f95
  note: propagated from a moved ground
- 2026-09-09T14:03:35-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "orphans" @54aa2e467954028f16a77e1a3d15d9d4b37a40ff
  note: read against commit 54aa2e4, which takes the ancestry memo, registers only readings that sit between the pin and HEAD, and asks the refutable half of a pointer the comparison has moved past; the rule is still asked of the ground, a refutable record still fails and an unconfirmable one still flags; the assertion holds as written.
- 2026-09-09T14:35:57-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "orphans" @54aa2e467954028f16a77e1a3d15d9d4b37a40ff
  artifact: 3a3a6a071a3744964776700d32117b8d23aad21d
  note: propagated from a moved ground
- 2026-09-09T14:35:57-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "orphans" @9d2289e8eaefecc7f3ac1132c9fa6934aae60e28
  note: read against commit 9d2289e, which collects moved_past by pointer rather than by position, so two readings at one commit are one baseline; the rule is still asked of the ground, a refutable record still fails and an unconfirmable one still flags; the assertion holds as written.
- 2026-09-10T22:05:55-07:00 · superseded · grade: measured · author: main
  evidence: entry: L0203-a-record-is-refuted-against-its-anchor-and-confirmed-against-the-tree · supersedes
  note: caused was removed: a record is refuted against the digest its anchor names and confirmed only by the tree in front of the run; the cohort widens to every propagated verdict

## References
