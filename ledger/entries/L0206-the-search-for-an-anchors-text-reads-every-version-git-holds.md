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

- 2026-09-11T19:30:01-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "digest_in_history" =sha256:75047ccad1a470ef72c17a05d8453b51ab1364e869757765003a8204c2ec4efa
  note: re-read after the commit that widens an object id to the repository's own hash width, and the reading records that this claim did not hold everywhere before it. The search reads every version of the path by collecting blob ids out of `git log --raw --no-abbrev`, and it filtered them through a forty-wide pattern: in a repository created with `--object-format=sha256` every id was discarded and no version was read at all, so a ground whose text had left the tree was reported as held by no version the repository has — the shallow-clone sentence's own failure mode, arrived at with the history intact. Measured in both formats before and after. The claim as written needs no change; the code now does what it says in either repository.
- 2026-09-15T17:25:46-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "digest_in_history" =sha256:75047ccad1a470ef72c17a05d8453b51ab1364e869757765003a8204c2ec4efa
  artifact: sha256:d3c7c028c30c1c1456e5f56bbe7294b8f72ef7e901e31366fc49e700fc00b968
  note: propagated from a moved ground

- 2026-09-15T17:26:29-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "digest_in_history" =sha256:d3c7c028c30c1c1456e5f56bbe7294b8f72ef7e901e31366fc49e700fc00b968
  note: re-read after the walk gained a `want_text` parameter, so that one pass of the history answers both the anchor that needs a yes and the held passage that needs the text. The walk itself is unchanged: the same `--all --full-history` log, the same object-id width taken from the repository, the same shallow-clone refusal.

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
