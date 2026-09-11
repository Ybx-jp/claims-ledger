---
id: L0205-an-anchor-by-value-resolves-to-text-in-the-tree-or-in-history
kind: claim
stated: 2026-09-11T02:37:27-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: bdabf00f6780f41440b0a51f65d62a5d1cf8bf084aadab1f5b2420b221835ba8
---

## Assertion

A ground anchored by value resolves when the text its effective anchor names is in the working tree; when it is not, an uncommitted entry fails, since the digest can still be recomputed, and a committed entry resolves if any version of the path the repository holds digests to the anchor and is flagged, not failed, when none does.

## Scope

metric: the outcome resolve gives a by-value ground whose anchor does not digest to the tree
cohort: every Grounds pointer of an evidence type whose anchor is stated by value, compared from its latest reading
condition: the placeholder anchor is excluded, since validate refuses it before any text is sought

## Grounds

- code: src/claims_ledger/resolve.py § "resolve_by_value" =sha256:779fef4bd8c45b1482f53a94c78750719f1ac1a6b2a89d689a3a812a332da89d

## Warrant

resolve_by_value asks the tree first and returns nothing when the section there digests to the anchor. When it does not, it branches on whether git holds the entry: an uncommitted entry fails, naming sha --write as the repair, because the hook is the moment a mistyped or stale digest can still be fixed and a wrong digest that landed would otherwise be flagged as moved on its first run and discharged by a reading of text nobody established a claim on; a committed entry is looked up in every version of the path, and returns nothing if one digests to the anchor. When no version does, the datum is still stated in full and freshness compares it exactly as before, so what is lost is only the diff a person would read during repair, and that is a flag rather than a failure. A git that could not say whether the entry is committed, or could not hand over the versions, is a failure that names the reason, never a silent pass.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/resolve.py · standing · cites-as-live
