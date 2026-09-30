---
id: L0308-an-anchor-is-decided-once-from-every-version-the-branch-holds
kind: claim
stated: 2026-09-24T22:15:43-07:00
author: main
grade: measured
supersedes: L0253-an-anchor-is-decided-once-from-the-branch-tip
verbatim_change: the Assertion now names every version of the artifact the branch holds, not only the tree at the tip, as where the answer is looked for; Scope is unchanged and there is no Backing
verbatim_sha: 6aac83f8efe9477875542cd5670971b1f8a90d7a0327a898b94514acda446689
---

## Assertion

A renumber decides each anchor once, before any commit is rebuilt, from the entries at the branch tip and every version of the anchored artifact the branch holds, and writes that same answer into every commit it rebuilds.

## Scope

metric: the anchor a rewritten entry carries across the commits of one rewrite
cohort: every by-value anchor a rewrite re-pins
condition: the entry appears in more than one commit of the branch

## Grounds

- code: src/claims_ledger/renumber.py § "decide_anchors" =sha256:16563fb253d3ecf7d236d9870923ee6295a2c336979d8a83bf037ec0168a507f

## Warrant

decide_anchors reads the entries at the tip once and hands reanchor every version of each anchored artifact the branch's commits hold, and reanchor records an answer for every anchor and applies a recorded answer before it asks anything else of the commit in hand; an entry's frozen region therefore cannot differ between two commits of one rewrite, which is what validate compares. Asking only the tip is not enough, because the text an anchor names need not be the text the tip holds.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
