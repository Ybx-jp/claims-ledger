---
id: L0269-a-lift-refuses-what-git-does-not-already-hold
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: a94cc2c67c52e802d1842fcd6773feae4a06d56123ee0d861c452718e64f4bd5
---

## Assertion

A lift refuses a file whose working tree differs from HEAD, so the prose it removes is bytes git already holds.

## Scope

metric: the condition a lift is attempted under
cohort: the file a lift would rewrite
condition: a working tree that differs from HEAD

## Grounds

- code: src/claims_ledger/lift.py § "refuse_unless_git_holds_it" =sha256:6a70136772748b51ed967a44472b0faaa988fe57aa2109a2550b3a39bf978161

## Warrant

Renumbering may rewrite a project's files because undoing its substitution reproduces what was there; a lift deletes, and nothing reconstructs a deletion from the file it left behind. What stands in for reversibility is that the bytes are in git before they are removed, so the witness has something to resolve against and a person has something to restore from.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/lift.py · standing · cites-as-live
- README.md · standing · cites-as-live
