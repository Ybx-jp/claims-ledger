---
id: L0101-a-path-is-put-to-git-as-a-literal-pathspec
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: eae23a9865768ef4bb466a1ffec541a24b8dcc0c2dfda8b84c1ef7a4f2bee913
---

## Assertion

A path is put to version control as a literal pathspec, so a wildcard character in a filename addresses only that file.

## Scope

metric: whether a glob character in an artifact's path can match another file
cohort: every comparison and history query naming an artifact
condition: paths are ordinary text in a pointer

## Grounds

- code: src/claims_ledger/freshness.py § "literal" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

literal wraps the path in the pathspec magic that says the text is a filename. Without it the brackets in a name like a numbered note are read as a character class, and an edit to an entirely different file — one no entry pins at all — was reported as this ground's drift. Every call in this checker that names a path goes through it, so the escape is established once rather than remembered at each site.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
