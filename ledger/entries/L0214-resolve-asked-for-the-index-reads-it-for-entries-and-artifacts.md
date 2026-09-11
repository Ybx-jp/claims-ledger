---
id: L0214-resolve-asked-for-the-index-reads-it-for-entries-and-artifacts
kind: claim
stated: 2026-09-11T14:12:08-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 2b5c053d076aeb67198cd1970d82e5a91aad91d689edb6311fac2fa1639b632f
---

## Assertion

The pointer resolver asked for the index reads the index for every question it puts to the tree — the entries it checks and the artifacts it holds them to — and a run whose index could not be read says it fell back to the working tree.

## Scope

metric: which tree resolve reads under the cached flag, for entries and for artifacts
cohort: every run of resolve invoked with the cached flag
condition: the entries and the artifacts are read from the same tree, and the fallback is reported rather than assumed

## Grounds

- code: src/claims_ledger/cli.py § "cmd_resolve" =sha256:c99492c2a57f3d30e9a84341f3aa5ad4877729bf274776774855ff7a33eb6929

## Warrant

cmd_resolve puts the flag to all three: the guard, so a fallback is named; load_entries, so the entries checked are the ones being committed; and resolve.run, so a by-value anchor is held to the artifact the commit will carry. Any one of the three left bare is a run answering about a state no commit contains — the working entry against the index's artifact, or the staged entry against the working tree's — and the answer is a pass, not a failure, so nothing downstream reports it. The three were wired together and are claimed together because a partial wiring is the shape that survives a test suite: before this, the cached path was reachable only from check, which the installed hook does not run, and dropping the flag from any of the three calls left every test green.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/cli.py · standing · cites-as-live
