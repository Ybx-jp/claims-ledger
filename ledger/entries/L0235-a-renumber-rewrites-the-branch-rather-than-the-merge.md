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

- 2026-09-14T20:21:10-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/renumber.py § "rewrite" =sha256:a7617476abb94765a512621eceb0ed9dddeeb4729901b20487f9d02f777c9506
  artifact: sha256:127c4df381a2225c36ff4f40bb433ec9d6913eff56dccff33ee216a6bce3dcd9
  note: propagated from a moved ground

- 2026-09-14T20:21:11-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/renumber.py § "rewrite" =sha256:127c4df381a2225c36ff4f40bb433ec9d6913eff56dccff33ee216a6bce3dcd9
  note: re-read after the commit that fixes what the pre-merge gate found. The section now carries an anchor decision across commits rather than taking it per commit. What this claim asserts is untouched: every commit is still rebuilt from its own tree with the entries renamed, so each renumbered entry is still added at the path it ends under and no commit in the rewritten history renames it.
- 2026-09-14T21:05:00-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/renumber.py § "rewrite" =sha256:127c4df381a2225c36ff4f40bb433ec9d6913eff56dccff33ee216a6bce3dcd9
  artifact: sha256:6cd425bf812e4e09ddcf364613942acceb419796dd3905cb185315335de957e1
  note: propagated from a moved ground

- 2026-09-14T21:05:02-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/renumber.py § "rewrite" =sha256:6cd425bf812e4e09ddcf364613942acceb419796dd3905cb185315335de957e1
  note: re-read after the commit that answers the gate's second round. The section now reads each commit's tree through a shared reader and takes the anchor decisions from a map computed before the loop. What this claim asserts is untouched: every commit is still rebuilt from its own tree with the entries renamed, so each renumbered entry is still added at the path it ends under.
- 2026-09-24T22:16:46-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/renumber.py § "rewrite" =sha256:6cd425bf812e4e09ddcf364613942acceb419796dd3905cb185315335de957e1
  artifact: sha256:9b3dc8e9d4b8136dec2db1f8d76ed7c7cb3ba8213843f7a178127308c528dd01
  note: propagated from a moved ground

- 2026-09-24T22:16:48-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/renumber.py § "rewrite" =sha256:9b3dc8e9d4b8136dec2db1f8d76ed7c7cb3ba8213843f7a178127308c528dd01
  note: re-read after #70. Each entry file is now also passed through refingerprint after it is re-anchored, which recomputes verbatim_sha where the substitution moved Scope or Backing, and reanchor is called with the decisions alone; which branch is rewritten, and that a moved entry is created under its new id rather than renamed, are unchanged.

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
- docs/OPERATING.md · standing · cites-as-live
