---
id: L0086-an-empty-repository-is-told-apart-from-an-unreadable-one
kind: claim
stated: 2026-09-08T02:30:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: be94edc73ea4f6b0b33d681ac32e8123be46c563da4795d354abf4443fce908d
---

## Assertion

A repository holding no commits is told apart from one that cannot be read: the empty repository is an ordinary state, and the unreadable one is a failure.

## Scope

metric: whether an empty repository and an unreadable one produce the same outcome
cohort: ledgers under a repository
condition: git log exits non-zero for both

## Grounds

- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_history asks rev-parse --verify --quiet HEAD before the walk and uses that answer to decide what an empty revision list means. Both conditions produce the same empty list out of git log, so collapsing them would either report a ledger being scaffolded as broken or pass a repository nothing could read. The question is asked once, at the top, rather than inferred from the walk's silence.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
