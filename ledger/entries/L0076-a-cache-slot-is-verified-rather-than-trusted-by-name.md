---
id: L0076-a-cache-slot-is-verified-rather-than-trusted-by-name
kind: claim
stated: 2026-09-08T02:26:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 144525517006f58f2e38e34ae35f67c4e5bde0be3a2f007d516bff61bd5f40a7
---

## Assertion

A content-addressed cache slot that already holds a file is verified against the digest rather than trusted by its name.

## Scope

metric: whether existing bytes under a cache slot are compared before being accepted
cohort: source bytes copied into the cache
condition: an interrupted registration can leave a file whose contents are not what its name says

## Grounds

- code: src/claims_ledger/authoring.py § "register_source" @c9f052af09e01b65a2adde51e941ebf24671dcaa

## Warrant

register_source hashes what is on disk and rewrites the slot unless it matches, and the copy goes through a temporary name so a second interruption cannot leave a third state. Trusting the name meant a retry exited 0 over bytes it never wrote, recording a row whose digest described something absent. The escape check runs ahead of that read, so a live link out of the root is refused rather than quietly accepted as a cache hit.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/authoring.py · standing · cites-as-live
