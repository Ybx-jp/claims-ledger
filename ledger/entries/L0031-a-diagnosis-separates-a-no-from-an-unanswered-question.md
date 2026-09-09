---
id: L0031-a-diagnosis-separates-a-no-from-an-unanswered-question
kind: claim
stated: 2026-09-08T02:02:27-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 4b99a8342ab5e19dfc490613a856538b3d32779b4ab52cbd105a096e062f1f3c
---

## Assertion

Every git question the failed-pointer diagnosis asks reports a negative answer and an unanswerable question as different outcomes, so no part of the diagnosis states as established what git declined to answer.

## Scope

metric: whether each git invocation in the diagnosis distinguishes a non-zero answer from a failure to run
cohort: evidence pointers that did not resolve
condition: git may be broken in one subcommand while the repository-level check passes

## Grounds

- code: src/claims_ledger/resolve.py § "why_not" @ec82c16045421ce5a6cb71befe8ddbe6067489ae

## Warrant

why_not reaches git through git_call, which carries the exit code and the reason separately, and it tests whether the code is absent before drawing any conclusion from a non-zero result. What it refuses to use is git()'s folding of the two into one None. The unasked gate in run asks rev-parse --git-dir and nothing more, so a git that answers there and fails in show reaches this function; a diagnosis built on the folded answer would tell a reader that a healthy commit lacks a path it has.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
