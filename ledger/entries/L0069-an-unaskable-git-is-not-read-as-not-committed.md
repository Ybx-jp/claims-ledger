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
- 2026-09-11T03:57:56-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "restamp" =sha256:462643362dd16beb66b7c055e703fda5f8d8a7cf2d2722a33eb4c2f2789f9c23
  artifact: sha256:240cbfdc8226c5395252e547b31e2754a27dbacca87e0fed67a4bf22bff8a774
  note: propagated from a moved ground
- 2026-09-11T03:58:17-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "restamp" =sha256:240cbfdc8226c5395252e547b31e2754a27dbacca87e0fed67a4bf22bff8a774
  note: read against the working tree after the fill of a pending anchor was narrowed to a Grounds line or a verdict's evidence line, since a Warrant sentence ending in the same text was being rewritten in the frozen region of a committed entry (qe gate, ticket c4e62619f4d5476f): an unasked git still raises before anything is written and the fingerprint is left alone; the assertion holds as written.
- 2026-09-20T15:29:16-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "is_committed" @225f5867b2591ffc5b3020dfe20ca407d81ee06f
  artifact: sha256:fd9312e13d08a2331bf9b6f92ef38c0968083bbc03d702926ff16ccc9b045807
  note: propagated from a moved ground

- 2026-09-20T15:29:16-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "restamp" =sha256:240cbfdc8226c5395252e547b31e2754a27dbacca87e0fed67a4bf22bff8a774
  artifact: sha256:dc432bfba68ca4abf7a71c020848faa150b2a34a30b9c5f0336d40c128d4accc
  note: propagated from a moved ground

- 2026-09-20T15:29:43-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "is_committed" =sha256:fd9312e13d08a2331bf9b6f92ef38c0968083bbc03d702926ff16ccc9b045807
  note: re-read after the commit that stops asking this question of HEAD alone. The answer now comes from a walk over every ref and every operation in progress, instead of `rev-parse --verify --quiet HEAD:<rel>`. What this claim asserts is unchanged: a git that could not be asked is still None and never a no — the walk failing is the one bit that says so.

- 2026-09-20T15:29:43-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "restamp" =sha256:dc432bfba68ca4abf7a71c020848faa150b2a34a30b9c5f0336d40c128d4accc
  note: re-read after the commit that widens what `is_committed` asks. This section calls it and is otherwise untouched; the call now takes the ledger rather than the repository, because the walk is kept on the ledger for the run. a git that could not be asked is still None and never a no — the walk failing is the one bit that says so.


## References

- src/claims_ledger/authoring.py · standing · cites-as-live
