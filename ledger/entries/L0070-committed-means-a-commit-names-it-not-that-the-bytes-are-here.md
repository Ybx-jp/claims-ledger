---
id: L0070-committed-means-a-commit-names-it-not-that-the-bytes-are-here
kind: claim
stated: 2026-09-08T02:26:33-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: bbe0c544e4607b21977dd26284b3fd720819a060a1fc7506b9021cf6f9ed5ccb
---

## Assertion

An entry counts as committed because a commit names it, and not because this checkout can still read its bytes.

## Scope

metric: the answer for an entry whose commit exists and whose blob is gone from the object store
cohort: entries under a repository
condition: the object store may be incomplete

## Grounds

- code: src/claims_ledger/authoring.py § "is_committed" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

is_committed asks rev-parse --verify, which resolves the path through the tree without requiring the object to be present. cat-file -e exits 1 in that case — an ordinary negative — and the entry would be treated as uncommitted and its frozen region rewritten. What makes the region immutable is that history names it; whether this working copy can still produce the bytes is a different question, and answering the second in place of the first is how a committed entry gets edited.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
