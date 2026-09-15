---
id: L0235-a-renumber-rewrites-the-branch-rather-than-the-merge
kind: claim
stated: 2026-09-14T19:13:42-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: f5363e9f3febef8c4620501700703acd2f49c6c36298b6a86f7d989a20c6005d
---

## Assertion

A renumber rewrites the branch that has not merged yet, so every entry it moves is created in that branch's own history under the id it will keep, and no entry file is renamed after a commit holds it.

## Scope

metric: the commit that creates each renumbered entry's path
cohort: every entry a renumber moves
condition: the branch is unmerged, which is the only branch this command will rewrite

## Grounds

- code: src/claims_ledger/renumber.py § "rewrite" =sha256:a7617476abb94765a512621eceb0ed9dddeeb4729901b20487f9d02f777c9506

## Warrant

rewrite replaces each commit of the branch with one built from the same tree with the ids substituted and the entries renamed, so the path an entry ends under is the path it is added at; no commit in the rewritten history renames it, and validate's comparison against the blob at the creating commit therefore covers the entry as it will stand.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
