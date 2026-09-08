---
id: L0099-git-is-the-arbiter-of-whether-a-pin-is-an-object-name
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 7f7af781e1f9b2d8ea1a64a39d5cdcbd5db7b9b3e8f72d27667cacf413c2020d
---

## Assertion

Whether a pin names an object rather than a moving name is settled by asking version control, for every pin and not only for the hex-shaped ones, and a question it could not answer is reported rather than read as a negative.

## Scope

metric: what decides whether a pin is an object name, and what an unanswerable question produces
cohort: the pin of every evidence ground
condition: the shape of the text settles it in neither direction

## Grounds

- code: src/claims_ledger/freshness.py § "is_object_name" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
- code: src/claims_ledger/freshness.py § "names_a_ref" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

is_object_name asks rev-parse --symbolic-full-name, which prints a fully qualified refname for a name and nothing for an object id. The text cannot decide it: a four-character hex string is a legal branch name, an uppercase object id is still an object id, and a tag name in a repository lacking that tag is neither. When the question cannot be answered at all the function says so separately, because reading that silence as `it is not a ref` would retire every unstable-pin flag in the ledger without a word.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
