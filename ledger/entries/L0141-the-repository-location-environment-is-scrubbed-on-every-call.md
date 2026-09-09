---
id: L0141-the-repository-location-environment-is-scrubbed-on-every-call
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: dd7123c8f72ea2c98cd117606a8b0f465fab44dff8b65f331a7de8bfbde501ab
---

## Assertion

The environment variables that tell version control which repository to use are removed from every call this package makes, and not only from the one that discovers the repository.

## Scope

metric: which calls run with the repository-location environment scrubbed
cohort: every version-control invocation in the package
condition: each call already names its repository directly

## Grounds

- code: src/claims_ledger/schema.py § "git_env" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "GIT_REPOSITORY_ENV" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "git_call" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

git_call builds its environment from git_env by default, so the scrub is a property of the call rather than an argument one site remembered to pass. Every variable in the list answers the question of which repository and where its parts are, which each call has already answered by naming the directory. Left in place they override that silently: measured against a ledger whose entry a commit already held, a rerouting variable let the fingerprint command rewrite that entry's frozen region at exit 0 and let the validator drop both immutability failures without a word. The whole documented group is taken rather than the three that were measured to bite, because a variable that reroutes the repository is a false pass waiting for a version that reads it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "GIT_REPOSITORY_ENV" @4af0acd253eeef1571cd7615ea3a041eda9e945e
  artifact: 36052faf227379aac7e17f339c1c6b3937d1f6c1
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "GIT_REPOSITORY_ENV" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed
- 2026-09-09T10:18:06-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "git_env" @4af0acd253eeef1571cd7615ea3a041eda9e945e
  artifact: c3a8a655fe9eae2546c56e64a2cf63e8493e27c6
  note: propagated from a moved ground

- 2026-09-09T10:18:16-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "git_env" @b73beb89121b47f1e945220810dfaae2c9ac4844
  note: read against this commit, which adds the tracing variables to what is dropped and pins the language. Neither touches this claim: the repository-location list is unchanged and still dropped on every call, and the index variable is still kept only where the index is the subject.

## References

- src/claims_ledger/schema.py · standing · cites-as-live
