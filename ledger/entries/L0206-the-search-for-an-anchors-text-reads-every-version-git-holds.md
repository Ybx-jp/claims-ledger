---
id: L0206-the-search-for-an-anchors-text-reads-every-version-git-holds
kind: claim
stated: 2026-09-11T02:37:27-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 5975f3c1336619524bc6e107cec4789d7bd0fdc982538283eab013a2b8368963
---

## Assertion

The search for the text a by-value anchor names reads every version of the path on every ref with full history, finds the section in each the way the comparison finds it, and reports a shallow clone's empty search as one that could not be made rather than as text that is gone.

## Scope

metric: which versions of the path are searched, and what an empty search means
cohort: every by-value Grounds pointer of a committed entry whose anchor does not digest to the tree
condition: the ledger sits in a git repository

## Grounds

- code: src/claims_ledger/resolve.py § "digest_in_history" =sha256:f002c72cdfbc9d3864cc7a09005f77563828b7e8fb76b3b6df1b80565fa78af4

## Warrant

digest_in_history lists the path's versions with log --all --full-history --raw, reads every blob id it names through one cat-file --batch, and compares the section extracted from each decoded blob by digest, so a version held on any branch or tag counts and a merge that kept one side is not skipped. A version git could not hand over is reported as a search that could not be made, and so is an empty search in a shallow clone, asked with rev-parse --is-shallow-repository: a clone at depth 1 has no object for a version that is perfectly well upstream, and reading its silence as text that is gone would flag every ground that moved before the graft boundary until the clone was deepened. Only a full search that finds nothing answers that the text is gone.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/resolve.py · standing · cites-as-live
