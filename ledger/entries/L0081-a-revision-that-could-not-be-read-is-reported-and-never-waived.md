---
id: L0081-a-revision-that-could-not-be-read-is-reported-and-never-waived
kind: claim
stated: 2026-09-08T02:30:44-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 423e9a1ec5d4f59bef03a518ce350562bbd2de95ac0993fc8f1ca95f97f2f2aa
---

## Assertion

A revision the append-only check could not read is reported as unchecked, rather than passed over as one across which nothing changed.

## Scope

metric: the outcome for a revision whose blob could not be read
cohort: revisions of an entry, their parents, and HEAD
condition: a parent git reports as missing is the revision the entry was created on

## Grounds

- code: src/claims_ledger/validate.py § "_unread_verdicts" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_history routes every unreadable blob through _unread_verdicts, which names the revision, the path and git's reason, and says that across that revision it was not checked that verdicts only appended. The single exception is a parent git calls missing, which is the edge the entry was created on and has nothing on its far side to compare. Waiving the rest would turn a git that could not answer into a clean run over history nobody read.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
