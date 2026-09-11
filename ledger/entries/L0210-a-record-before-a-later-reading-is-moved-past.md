---
id: L0210-a-record-before-a-later-reading-is-moved-past
kind: claim
stated: 2026-09-11T03:57:02-07:00
author: main
grade: measured
supersedes: L0203-a-record-is-refuted-against-its-anchor-and-confirmed-against-the-tree
verbatim_change: condition gains a drift committed and then reverted; Backing unchanged
verbatim_sha: cc1063724c8d97062ba5a012a43880fa5fbf3e51ed555d03f83aa630f6ee2313
---

## Assertion

A propagated verdict recording the digest its pointer's anchor names fails as refuted on any pointer; one recording something this run does not see, on a ground that is fresh where it is compared from, flags as unconfirmable unless a corroborating reading of the ground sits after it in the file, whatever pointer either names; nothing is asked of history.

## Scope

metric: the outcome for each of the two ways a recorded artifact is not confirmed
cohort: every propagated verdict naming a checked ground
condition: an ordinary drift may be recorded and then abandoned before it is committed, or committed and then reverted

## Grounds

- code: src/claims_ledger/freshness.py § "orphans" =sha256:95d53991b186a3f20d33f2f9a16b06da68d7d68547d9cb4505b87d0d767b2158

## Warrant

orphans compares each record against the digest anchor_digest gives for the pointer the verdict names, and fails the entry when they are equal, since such a record states no drift at all; that is the pre-emptive forgery the rule was written for, and it is asked of every verdict so that a real drift and a later reading cannot carry the accusation away. For the rest it keeps, per pointer the ground has been compared from, the index of the latest reading of the ground, and holds only the records with a higher index to what this run sees: a record before a reading was looked at when the reading was made, whatever the reading names, and a record after it on a ground that is fresh where it is compared from is what an ordinary drift looks like when it is never committed or is undone, flagged rather than failed since failing it left a permanent red no legal edit could clear. Keyed on the pointer's text rather than its position, a drift committed and then reverted left a flag that only a reading of the ground's own digest could clear, and that reading was refused.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/freshness.py · standing · cites-as-live
- docs/FRESHNESS.md · standing · cites-as-live
