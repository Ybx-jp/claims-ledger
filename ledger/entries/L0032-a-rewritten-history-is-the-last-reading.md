---
id: L0032-a-rewritten-history-is-the-last-reading
kind: claim
stated: 2026-09-08T02:02:27-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 04c16a2f591d3a02b95bc7d95d3aa2a74f00eddae51c4393223e99f54c6d4185
---

## Assertion

A pin git has no object for is reported as a commit dropped by a rewritten history only after three other explanations are ruled out: that the pin is not an object name, that it abbreviates several objects, and that the clone is shallow.

## Scope

metric: the conditions that must hold before the dropped-commit diagnosis is printed
cohort: evidence pins git cannot resolve to an object
condition: the repository may be shallow, and the pin may be an ambiguous abbreviation

## Grounds

- code: src/claims_ledger/resolve.py § "why_not" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
- code: src/claims_ledger/resolve.py § "OBJECT_NAME" @ec82c16045421ce5a6cb71befe8ddbe6067489ae

## Warrant

The dropped-commit sentence is the last return of why_not, and each earlier return takes one alternative away. OBJECT_NAME admits only bare hex names, so a revision expression such as a deleted branch is answered as one git cannot resolve here rather than as history loss. Ambiguity is settled by asking rev-parse --disambiguate for the candidate names rather than by reading git's error text, which is the same line for an absent object as for an ambiguous prefix. A shallow clone is named as such, because a commit outside the graft boundary is missing here and perfectly well upstream. The reading that costs a supersession per pinned ground is reached only when nothing cheaper explains the silence.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-20T18:08:44-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "why_not" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
  artifact: sha256:c83756cbb8de1bd35d7b459aad0f1ed0181c70be336d0a51754135b6a73b9368
  note: propagated from a moved ground

- 2026-09-20T18:08:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "why_not" =sha256:c83756cbb8de1bd35d7b459aad0f1ed0181c70be336d0a51754135b6a73b9368
  note: Same edit, read against a different claim: the diagnosis this entry is about is unchanged, and only the document path at the end of one message became a resolved one. Nothing here decides a diagnosis from it.

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
