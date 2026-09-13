---
id: L0142-the-index-variable-is-kept-only-where-the-index-is-the-subject
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: dd87f32094eb6fd1f4cfbd6e91a435a522f32f3126546a3e4d5465e5b6742952
---

## Assertion

The variable naming which index to read is kept for exactly the calls whose subject is the index, and removed from every other call.

## Scope

metric: which calls see the index-location variable
cohort: calls made under the cached mode, and all others
condition: a commit hook is given the index the commit is being built in

## Grounds

- code: src/claims_ledger/schema.py § "git_env" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

git_env drops the whole repository-location group and puts that one variable back only when asked. Under a hook, a partial commit builds a temporary index holding the tip plus the named paths, not the ordinary one; scrubbing the variable there would take the two cached checkers off the content being committed and onto content that is not, which is the same false pass as the rest of the list pointed the other way. So the one question this package asks of the environment is asked by the callers whose subject it is, and by no others.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-09T10:18:06-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "git_env" @4af0acd253eeef1571cd7615ea3a041eda9e945e
  artifact: c3a8a655fe9eae2546c56e64a2cf63e8493e27c6
  note: propagated from a moved ground

- 2026-09-09T10:18:17-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "git_env" @b73beb89121b47f1e945220810dfaae2c9ac4844
  note: read against this commit, which adds the tracing variables to what is dropped and pins the language. Neither touches this claim: the repository-location list is unchanged and still dropped on every call, and the index variable is still kept only where the index is the subject.
- 2026-09-11T13:35:33-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "git_env" @b73beb89121b47f1e945220810dfaae2c9ac4844
  artifact: sha256:c087a08faabe59becc1684ea54899cfd2b1227e36c80ae6fad7d215c036dcbd5
  note: propagated from a moved ground

- 2026-09-11T13:36:03-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "git_env" =sha256:c087a08faabe59becc1684ea54899cfd2b1227e36c80ae6fad7d215c036dcbd5
  note: read against the commit that gives resolve a cached mode, making three callers ask for the index where two did. The claim is unaffected: the variable is still kept for exactly the calls whose subject is the index and removed from every other call, and the code deciding that is byte-identical. The Warrant's 'the two cached checkers' is now a stale count, frozen where it stands; the rule it argues for is unchanged.

- 2026-09-11T14:15:11-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "git_env" =sha256:fdf0922f5d91edf99f7b8083db4ece44b25c58d7528717a965fd29691be79656
  note: re-read after the same docstring was rewrapped to the line limit the linter holds; the prose is unchanged in substance and the code in this section is byte-identical, so nothing this claim rests on moved.

- 2026-09-11T17:11:14-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "git_env" =sha256:88c1e210b0a22ec11e9349553777e856ee7899d1992ab20c15519c468f024a04
  note: re-read after the commit that adds the pathspec-interpretation variables to what this call drops. GIT_INDEX_FILE is still the one variable discarded from the drop set, still only under `index=True`, and the new group is dropped unconditionally, so the exception this claim is about is untouched.

- 2026-09-11T19:41:48-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "git_env" =sha256:4988936b31fa54b9cfd7a9841c39a5e812c03b7e1f4314490d134d8c4ba3c351
  note: re-read after the same commit. The docstring's count of the checkers the hook runs with the flag is now all five where it said three; which variables are dropped and which one is kept, and under what condition, are untouched.

## References

- src/claims_ledger/schema.py · standing · cites-as-live
