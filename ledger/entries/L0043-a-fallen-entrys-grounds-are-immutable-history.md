---
id: L0043-a-fallen-entrys-grounds-are-immutable-history
kind: claim
stated: 2026-09-08T02:08:33-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9b582f4d9fb2892ea5058d75aac59b6e4446b84f88b802f17bae4cf362fa707e
---

## Assertion

The grounds of an entry whose own status has fallen are exempt from the act check, so a refuted, superseded or retracted entry is not reported for citing a target that fell after it.

## Scope

metric: whether the grounds of a fallen entry are held to their targets' current statuses
cohort: entries whose derived status is refuted, superseded or retracted
condition: such an entry holds a ground citing a target that has since fallen

## Grounds

- code: src/claims_ledger/references.py § "run" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487
- code: src/claims_ledger/schema.py § "FALLEN" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487

## Warrant

run tests an entry's status against FALLEN and skips it before reading its grounds at all. A fallen entry's Grounds are the record of what it rested on when it was stated, and editing them to satisfy a checker would destroy the history the ledger exists to keep. The repair for a dependent whose live-cited ground fell is a successor, and it is the successor's acts that are held to the targets' current statuses.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/references.py · standing · cites-as-live
