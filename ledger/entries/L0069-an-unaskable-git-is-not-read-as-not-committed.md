---
id: L0069-an-unaskable-git-is-not-read-as-not-committed
kind: claim
stated: 2026-09-08T02:26:28-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 122ed287ffecc610bb07d743bcc13ceee31b77a1db630a8ea319dae32d005135
---

## Assertion

A git that could not be asked whether an entry is committed is reported as unasked rather than read as an answer, and the fingerprint is left alone.

## Scope

metric: what an unanswerable git produces when a fingerprint is about to be rewritten
cohort: the command that recomputes verbatim_sha
condition: git may be absent, or present and unable to read the object

## Grounds

- code: src/claims_ledger/authoring.py § "is_committed" @c9f052af09e01b65a2adde51e941ebf24671dcaa
- code: src/claims_ledger/authoring.py § "restamp" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

is_committed returns the reason separately from the answer: it clears the repository with git_problem, then asks rev-parse --verify --quiet, which exits 1 for a path HEAD lacks and 128 for a git that could not look. restamp turns that reason into a refusal naming it and writes nothing unless forced. Folded into one None — which is all the plain git helper offers — the two become the same thing, and a fingerprint rewrite with git off PATH edited the frozen region of a committed entry and exited 0.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
