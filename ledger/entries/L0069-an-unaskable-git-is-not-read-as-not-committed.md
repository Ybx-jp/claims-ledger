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

- 2026-09-08T19:39:25-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "is_committed" @c9f052af09e01b65a2adde51e941ebf24671dcaa
  artifact: 49b0d15829c079f80cbe0d7f5887d37f54e8bed2
  note: propagated from a moved ground

- 2026-09-08T19:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "is_committed" @225f5867b2591ffc5b3020dfe20ca407d81ee06f
  note: read against commit 225f586, which moved `ARCH-AUDIT.md` into `docs/audits/` and rewrote the mentions of it in this section; the section was parsed at the pin and at that commit and compared with comments and docstrings set aside, and the two are identical, so nothing the claim rests on changed
- 2026-09-11T02:56:08-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "restamp" @c9f052af09e01b65a2adde51e941ebf24671dcaa
  artifact: sha256:462643362dd16beb66b7c055e703fda5f8d8a7cf2d2722a33eb4c2f2789f9c23
  note: propagated from a moved ground
- 2026-09-11T02:56:26-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "restamp" =sha256:462643362dd16beb66b7c055e703fda5f8d8a7cf2d2722a33eb4c2f2789f9c23
  note: read against the working tree after sha --write began filling `=?` anchors: an unasked git still raises before anything is written, now for an anchor in the Grounds as well as for the fingerprint, and the fingerprint is left alone; the assertion holds as written.

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
