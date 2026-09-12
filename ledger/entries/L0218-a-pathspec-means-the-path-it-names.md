---
id: L0218-a-pathspec-means-the-path-it-names
kind: claim
stated: 2026-09-11T17:09:07-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 331a6ea9d3b2455077327d6c4614ddee34fa30bfd5bd2272750ec5c8991dbad9
---

## Assertion

The environment variables that decide how version control reads a pathspec are removed from every call this package makes, so a path written as a literal is asked about as the path it names.

## Scope

metric: which calls run with the pathspec-interpretation environment scrubbed
cohort: every version-control invocation in the package
condition: what a call then does with the answer is that caller's own claim

## Grounds

- code: src/claims_ledger/schema.py § "GIT_PATHSPEC_ENV" =sha256:b798e288ddb48b8a99ca61ef1751361c369bfee315fc02366b4802dd4389ee27
- code: src/claims_ledger/schema.py § "git_env" =sha256:88c1e210b0a22ec11e9349553777e856ee7899d1992ab20c15519c468f024a04
- entry: L0141-the-repository-location-environment-is-scrubbed-on-every-call · distinguishes
- entry: L0142-the-index-variable-is-kept-only-where-the-index-is-the-subject · distinguishes
- entry: L0194-git-is-asked-in-one-language-and-told-not-to-trace · distinguishes

## Warrant

Two calls here write a path as `:(literal)<path>`, because a path is a filename and not a wildcard, and one variable unwrites that: with GIT_LITERAL_PATHSPECS exported, git reads the whole pathspec literally and looks for a file whose name begins with a parenthesis. Nothing has ever been at that path, so the answer comes back clean and empty rather than as an error — and both callers read empty as news. Measured on git 2.43.0 against a ledger an enclosing repository had committed: with the variable set, validate went from exit 1 naming an immutable region to 0 failures with nothing said, because the walk read "no commit has touched these entries" as "no repository holds them". Freshness loses less and still reports the drift, because it compares digests rather than asking history, but its account of the drift becomes uncommitted when a commit is what moved it. The whole documented group of four is dropped rather than the one measured to bite, on the same reasoning the repository-location list is taken whole: a variable that decides what a pathspec means is a false pass waiting for a git version that reads it, and no caller here wants one. The three entries named above hold other rules over the same section — which repository, which index, which language — and this is a fourth, not a reading of any of them.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-11T19:41:48-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "git_env" =sha256:4988936b31fa54b9cfd7a9841c39a5e812c03b7e1f4314490d134d8c4ba3c351
  note: re-read after the same commit. The docstring's count of the checkers the hook runs with the flag is now all five where it said three; which variables are dropped and which one is kept, and under what condition, are untouched.

## References

- src/claims_ledger/schema.py · standing · cites-as-live
