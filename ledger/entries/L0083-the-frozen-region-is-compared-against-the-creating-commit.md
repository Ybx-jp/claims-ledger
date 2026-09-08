---
id: L0083-the-frozen-region-is-compared-against-the-creating-commit
kind: claim
stated: 2026-09-08T02:30:45-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 183b56f4ed3cd68c891c93dabb12584d984495b9e1b7f89001f191a313c246cf
---

## Assertion

An entry's frozen region is compared against the blob at the commit that created the file, and not against its most recent revision.

## Scope

metric: which revision the frozen region is held to
cohort: committed entries
condition: an entry may have many revisions, all of them appends

## Grounds

- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_history takes the oldest revision the walk found for the path and reads the blob there. Comparing against the previous revision instead would make an edit to the frozen region permanent the moment it survived one commit. Comparing against the creating commit holds the region to what it was when the entry entered history, which is what the immutability the ledger promises actually says.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
