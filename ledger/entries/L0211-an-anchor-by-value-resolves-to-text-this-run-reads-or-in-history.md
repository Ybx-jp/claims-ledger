---
id: L0211-an-anchor-by-value-resolves-to-text-this-run-reads-or-in-history
kind: claim
stated: 2026-09-11T03:57:51-07:00
author: main
grade: measured
supersedes: L0205-an-anchor-by-value-resolves-to-text-in-the-tree-or-in-history
verbatim_change: metric and condition now name the tree this run reads, the index under --cached; Backing unchanged
verbatim_sha: a34ce7ee1b1d9ad98d3b89c4f69e782a3d43b1b9374690c0a9fbc73c0fc0ec23
---

## Assertion

A ground anchored by value resolves when the text its effective anchor names is in the tree this run reads, the working tree or the index under --cached; when it is not, an uncommitted entry fails, since the digest can still be recomputed, and a committed entry resolves if any version of the path the repository holds digests to the anchor and is flagged, not failed, when none does.

## Scope

metric: the outcome resolve gives a by-value ground whose anchor does not digest to the tree this run reads
cohort: every Grounds pointer of an evidence type whose anchor is stated by value, compared from its latest reading
condition: the placeholder anchor is excluded, since validate refuses it before any text is sought; under --cached the index is read, as freshness reads it

## Grounds

- code: src/claims_ledger/resolve.py § "resolve_by_value" =sha256:5c6f76d89b689f0f4acf9413d3b6992ede5f4a47441fd1b3dfbb852bf00faa65
- code: src/claims_ledger/resolve.py § "digest_in_tree" =sha256:1b7be15bf39229a275c3175bab5378650c20ab608f8cb00c521a0664e06d7011

## Warrant

resolve_by_value asks digest_in_tree first and returns nothing when the section there digests to the anchor; digest_in_tree reads the working tree, or under --cached the index through git as freshness does, because the hook runs check --cached and a read of the working tree there answered for a file staged in one state and left in another, so the entry landed with an anchor no version of the path holds. When the text is not there, it branches on whether git holds the entry: an uncommitted entry fails, naming sha --write, because this is the moment a mistyped or stale digest can still be fixed and a wrong digest that landed would otherwise be flagged as moved on its first run and discharged by a reading of text nobody established a claim on; a committed entry is looked up in every version of the path, and returns nothing if one digests to the anchor. When no version does, the datum is still stated in full and freshness compares it exactly as before, so what is lost is only the diff a person would read during repair, and that is a flag rather than a failure. A git that could not say whether the entry is committed, or could not hand over the versions, is a failure that names the reason, never a silent pass.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-11T13:35:33-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "digest_in_tree" =sha256:1b7be15bf39229a275c3175bab5378650c20ab608f8cb00c521a0664e06d7011
  artifact: sha256:6d0ede392a0e4991eb4d795b1565967b5f8252ad3fc1b108f17a03079b295380
  note: propagated from a moved ground

- 2026-09-11T13:36:03-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "digest_in_tree" =sha256:6d0ede392a0e4991eb4d795b1565967b5f8252ad3fc1b108f17a03079b295380
  note: read against the commit that gives resolve a --cached of its own and points the hook's resolve line at it. What this claim asserts is unchanged and the code is byte-identical: the index under --cached, the working tree otherwise. The Warrant named that hook line `check --cached`, which the installed hook never ran; it runs `resolve --cached`.

## References
- src/claims_ledger/resolve.py · standing · cites-as-live
