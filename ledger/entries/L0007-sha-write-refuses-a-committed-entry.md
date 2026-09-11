---
id: L0007-sha-write-refuses-a-committed-entry
kind: claim
stated: 2026-09-07T13:30:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: f116faacee4e27ef92166f0bcd2309462802c5210039b29c3b07e56c125db046
---

## Assertion

sha --write refuses to rewrite the fingerprint of an entry git already has, and of an entry whose commit state git could not establish, unless --force is passed.

## Scope

metric: whether sha --write rewrites verbatim_sha
cohort: entries under the ledger's entries directory
condition: the entry is in a commit, or whether it is could not be established

## Grounds

- code: src/claims_ledger/authoring.py § "restamp" @4023af4006273319aec9ae2512d197e4a99fce8c

## Warrant

restamp asks is_committed before writing and raises AuthoringError both for a committed entry and for an unanswered question, in each case unless force is set.

## Backing

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-11T02:56:08-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "restamp" @4023af4006273319aec9ae2512d197e4a99fce8c
  artifact: sha256:462643362dd16beb66b7c055e703fda5f8d8a7cf2d2722a33eb4c2f2789f9c23
  note: propagated from a moved ground
- 2026-09-11T02:56:26-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "restamp" =sha256:462643362dd16beb66b7c055e703fda5f8d8a7cf2d2722a33eb4c2f2789f9c23
  note: read against the working tree after sha --write began filling `=?` anchors: the committed and unasked refusals are unchanged in wording and in when they fire for a new fingerprint, and are now also asked before a Grounds anchor is filled, since that is the same frozen region; --force still lifts both; the assertion holds as written.
- 2026-09-11T03:57:56-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/authoring.py § "restamp" =sha256:462643362dd16beb66b7c055e703fda5f8d8a7cf2d2722a33eb4c2f2789f9c23
  artifact: sha256:240cbfdc8226c5395252e547b31e2754a27dbacca87e0fed67a4bf22bff8a774
  note: propagated from a moved ground
- 2026-09-11T03:58:17-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/authoring.py § "restamp" =sha256:240cbfdc8226c5395252e547b31e2754a27dbacca87e0fed67a4bf22bff8a774
  note: read against the working tree after the fill of a pending anchor was narrowed to a Grounds line or a verdict's evidence line, since a Warrant sentence ending in the same text was being rewritten in the frozen region of a committed entry (qe gate, ticket c4e62619f4d5476f): the committed and unasked refusals are unchanged, and --force still lifts both; the assertion holds as written.

## References

- README.md · standing · cites-as-live
- src/claims_ledger/authoring.py · standing · cites-as-live
