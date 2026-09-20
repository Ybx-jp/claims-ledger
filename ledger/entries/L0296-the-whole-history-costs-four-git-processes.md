---
id: L0296-the-whole-history-costs-four-git-processes
kind: claim
stated: 2026-09-20T15:23:32-07:00
author: main
grade: measured
supersedes: L0084-the-whole-history-costs-three-git-processes
verbatim_sha: 893c84b73b5944d9c6dcfb6b8be225579186311e4021da89caa3f64f2ce5b1f1
---

## Assertion

The whole ledger's history is read with four git processes: one asking whether anything is committed, one asking where the git directory is, one walk of the entries directory, and one batch reading every blob the walk named.

## Scope

metric: the number of git processes a history check starts
cohort: a validate run over a ledger of any size
condition: the count is expected to stay flat as entries and revisions grow

## Grounds

- code: src/claims_ledger/validate.py § "check_history" =sha256:a8dc0b278ba056161297d7bfb4a6899f044b8da899aa83d7a8b9599271e9d6f6
- code: src/claims_ledger/schema.py § "git_history" =sha256:9b955321cb089f1a73a48a3214182c115527f9086cf0f61ebe4a868605ea4c76
- code: src/claims_ledger/schema.py § "git_blobs" =sha256:242a5aaec1f5d3c4e461fff7e1cba2ae548cc3af5e350250789ebbf98ee50250
- code: src/claims_ledger/schema.py § "heads_in_progress" =sha256:9779a326ae670a1e6419a44734a968cead7b88808057bafaf7b0639da9b9edcb

## Warrant

Three of the four are what the predecessor counted and are unchanged. The fourth asks git where its directory is, so that the walk can be pointed at the other side of an operation in progress as well as at HEAD; it is asked once and kept on the ledger, so the property the count is really about — flat as entries and revisions grow — is what it was. The number is stated as well as the flatness because a check that compares one size against another stays green while a process is added, which is how the predecessor went on being cited as live after a branch added one.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
