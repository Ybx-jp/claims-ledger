---
id: L0227-an-unanswered-index-read-is-not-an-absent-path
kind: claim
stated: 2026-09-11T22:03:28-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 749a114d783ef7d02f4884d2230ae522a53e9237c22b6fee97c7366d0ffd4233
---

## Assertion

A read of the index that version control did not answer is told apart from version control saying the index does not hold that path, and only the second is read as absence.

## Scope

metric: whether a failed index read is distinguished from an absent path
cohort: every read of a staged blob under the cached flag
condition: what each caller then does with the distinction is that caller's own claim

## Grounds

- code: src/claims_ledger/schema.py § "blob_absent" =sha256:eb6e7abf3a58cd7b650238899745633b971c6e1240a5a98d2d0fef937983ec83
- entry: L0031-a-diagnosis-separates-a-no-from-an-unanswered-question · distinguishes

## Warrant

Every staged read folded the two together, and the fold is a false pass with nothing in the output to look at: a path the reader believes is not staged is read from the working tree instead, and the run reports on a tree the commit will not carry. Measured with a version control binary that fails only its batch read — a timeout, a pack it cannot open, a process killed, each reaching the code this way — the pointer checker went from exit 1 naming a staged withdrawal to a clean run over nothing. The batch reader already knows the difference and says so in the reason it returns; what was missing was a caller asking. Four readers rest on this and each was measured to be held by nothing before the tests written with it: the entry list, the source registry, the configured documents, and a ground pinned at working. The entry named above holds the same rule for what version control says about a commit rather than about the index.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
