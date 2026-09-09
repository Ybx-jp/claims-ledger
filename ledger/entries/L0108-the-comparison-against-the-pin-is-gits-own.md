---
id: L0108-the-comparison-against-the-pin-is-gits-own
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 92ef3afb58d499124d053dbba0c1147f3997ec63739d5bfa1383a2edfe531328
---

## Assertion

The artifact is compared against the pin by version control's own comparison, so filters and line endings are applied to both sides alike.

## Scope

metric: what performs the comparison between the pin and the tree being read
cohort: every pinned evidence ground
condition: the tree read is the working tree, or the index under --cached

## Grounds

- code: src/claims_ledger/freshness.py § "drift" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

drift asks for a name-only diff between the pin and the tree this run is reading, rather than comparing bytes itself. Whatever the repository does to a file on its way in and out — line endings, clean filters — is then done to both sides, so a difference reported is a difference the repository itself sees. Empty output means the path is unchanged, and no section inside it can have moved either, so the text is never read at all.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
