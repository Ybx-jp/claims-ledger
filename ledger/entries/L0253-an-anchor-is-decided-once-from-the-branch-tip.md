---
id: L0253-an-anchor-is-decided-once-from-the-branch-tip
kind: claim
stated: 2026-09-14T21:04:01-07:00
author: main
grade: measured
supersedes: L0252-an-anchor-is-decided-once-for-the-whole-rewrite
verbatim_sha: 6aac83f8efe9477875542cd5670971b1f8a90d7a0327a898b94514acda446689
---

## Assertion

A renumber decides each anchor once, from the tree at the branch tip, and writes that same answer into every commit it rebuilds.

## Scope

metric: the anchor a rewritten entry carries across the commits of one rewrite
cohort: every by-value anchor a rewrite re-pins
condition: the entry appears in more than one commit of the branch

## Grounds

- code: src/claims_ledger/renumber.py § "decide_anchors" =sha256:19de168cc85ba138538f26c7bd4300dc723e89778547cf9b57f7b54bc8b737d0

## Warrant

decide_anchors reads the tip once and records an answer for every anchor it finds there, and reanchor applies a recorded answer before it asks anything else of the commit in hand; an entry's frozen region therefore cannot differ between two commits of one rewrite, which is what validate compares. Deciding where the entry is created is not enough, because the artifact a ground names may arrive in a later commit of the same branch and there is then no answer to be had at the earlier one.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-24T22:16:06-07:00 · superseded · grade: measured · author: main
  evidence: entry: L0308-an-anchor-is-decided-once-from-every-version-the-branch-holds · supersedes
  note: the answer is now looked for in every version of the artifact the branch holds, not only the tree at the tip, because the text an anchor names need not be the tip's. What is unchanged is that each anchor is decided once and the same answer goes into every commit.

## References

