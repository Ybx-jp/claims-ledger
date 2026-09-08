---
id: L0087-rename-detection-is-off-because-an-entry-is-never-renamed
kind: claim
stated: 2026-09-08T02:30:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 65e0241cd2a42b9683d29244f895a0fe734c88914fa3666ade200cd7d480cd78
---

## Assertion

The history walk runs without rename detection, because an entry is never renamed: its id is its filename.

## Scope

metric: whether the walk asks git to follow renames
cohort: the history walk under the entries directory
condition: a successor is often written as a near-copy of its predecessor

## Grounds

- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

git_history is called without --follow. Rename detection compares each file against every file in the parent commit, so a successor written as a near-copy of a predecessor still in the tree is reported as renamed from it, and the creating commit comes back as one where this file did not exist — leaving the frozen-region comparison reading the wrong blob entirely. An entry's filename is its id and does not change, so there is nothing here for the detection to find and everything for it to invent.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
