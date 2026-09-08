---
id: L0030-an-unaskable-git-is-reported-once-for-the-ledger
kind: claim
stated: 2026-09-08T02:02:20-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 31c94b00fb9cff8e408bf8b37061ce7a76ceaeaaa8288eb2e61080ca5d46aad6
---

## Assertion

When git cannot be asked at all, the run says so once for the whole ledger and leaves every pinned pointer unjudged, rather than reporting each of them as a pointer that does not resolve.

## Scope

metric: the number of reports emitted for an unavailable git, and what each pinned pointer is then said to be
cohort: ledgers holding at least one pinned evidence pointer
condition: git absent from PATH, or present and unable to answer for the repository

## Grounds

- code: src/claims_ledger/resolve.py § "run" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
- code: src/claims_ledger/resolve.py § "resolve_pointer" @ec82c16045421ce5a6cb71befe8ddbe6067489ae

## Warrant

run asks git_problem once, and only when some entry actually holds a pinned pointer; the answer becomes a single Grounds-level failure saying the pins were not read out of git and that whether each still names its artifact is unknown. That same answer is handed to resolve_pointer, which returns without judging any pinned pointer. The unavailability is therefore reported as unavailability, and no pin is described as unresolved on the strength of a question git never answered.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
