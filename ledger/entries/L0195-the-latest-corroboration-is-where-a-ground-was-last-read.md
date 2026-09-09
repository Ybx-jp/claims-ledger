---
id: L0195-the-latest-corroboration-is-where-a-ground-was-last-read
kind: claim
stated: 2026-09-09T13:23:20-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 01fd027edb8d31b41f417e82a1e5705df587889492b9dcf8c87d9ffb415d04a1
---

## Assertion

A ground is compared from the latest corroborating verdict that names its section at a commit, and from its pin only until one exists, so a change after an acknowledged reading is reported again.

## Scope

metric: which revision a ground's section is compared against for drift
cohort: every pinned ground of a live entry, under freshness
condition: the corroboration names the same type, path and section, at a commit rather than an unpinned reference

## Grounds

- code: src/claims_ledger/freshness.py § "effective_pointer" @9d54a2f75fffcbc9b1c21199099c0bf6fa6060ab

## Warrant

effective_pointer walks the entry's verdicts in order and keeps the last well-formed corroborated one whose pointer matches the ground's type, target and section and whose pin is a commit under a compared type; run compares from that pointer, writes a new drift against it, and orphans holds a propagated verdict to the history since it. The pin is frozen and discharges() asks whether an acknowledged artifact was ever held between the pin and here, a range that only grows, so without a reference point that advances a ground acknowledged once was silent for the life of its entry: measured on this ledger before the change, 93 of 270 live grounds were in that state and 49 had moved again since the reading that silenced them. The corroborating verdict is that reference point because validate already forbids it from restating a ground, so its evidence is a fresh reading at a later commit.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-09T13:28:16-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "effective_pointer" @9d54a2f75fffcbc9b1c21199099c0bf6fa6060ab
  artifact: d3839ddf380073c420e1b127e402cf5d058cad26
  note: propagated from a moved ground
- 2026-09-09T13:28:16-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "effective_pointer" @825902da5293a5d7121cfa0a7b9cc6d3d4eb5ef0
  note: read against commit 825902d, which takes the last of the readings `readings` lists rather than walking the verdicts itself; which verdict counts as a reading, and that the Ground is compared from its pin until one exists, are unchanged; the assertion holds as written.

## References
- src/claims_ledger/freshness.py · standing · cites-as-live
