---
id: L0260-a-stored-passage-line-carries-its-own-indentation
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 209c60646607d440a68682570fbf434546e08785559260b14019f3d88f926f63
---

## Assertion

A stored passage line carries the artifact's own indentation on top of the six spaces the format adds, so stripping those six returns the prose as the artifact held it.

## Scope

metric: what a stored passage line is made of
cohort: the passage lines of a Passages block
condition: prose lifted from an indented artifact

## Grounds

- code: src/claims_ledger/schema.py § "PASSAGE_INDENT" =sha256:829b6fa0ceba86ee22d6ff8ddfd1f368f570e753e755227f0c074c072198504e
- code: src/claims_ledger/schema.py § "_passage_text" =sha256:2720a759fe6ea93e2f33513d9d8b7d7d89700db3cbc94c7fdafd78038e0a0a06

## Warrant

A docstring body indented four spaces is stored at ten and read back at four. A blank line is stored blank rather than as six spaces, because a line of trailing whitespace is not what was lifted, and both the store and the comparison strip trailing whitespace so the two never disagree about it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
