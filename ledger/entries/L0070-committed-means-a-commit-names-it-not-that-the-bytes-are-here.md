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

- 2026-09-08T19:39:25-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "is_committed" @c9f052af09e01b65a2adde51e941ebf24671dcaa
  artifact: 49b0d15829c079f80cbe0d7f5887d37f54e8bed2
  note: propagated from a moved ground

- 2026-09-08T19:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "is_committed" @225f5867b2591ffc5b3020dfe20ca407d81ee06f
  note: read against commit 225f586, which moved `ARCH-AUDIT.md` into `docs/audits/` and rewrote the mentions of it in this section; the section was parsed at the pin and at that commit and compared with comments and docstrings set aside, and the two are identical, so nothing the claim rests on changed

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
