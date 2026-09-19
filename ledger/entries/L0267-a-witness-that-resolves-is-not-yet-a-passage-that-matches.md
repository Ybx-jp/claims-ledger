---
id: L0267-a-witness-that-resolves-is-not-yet-a-passage-that-matches
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 01a175118c588f7f71c991c81f7ac30510a55170d22468102b3a6d4cda0ec63f
---

## Assertion

A passage is compared against the version its witness found, so prose the artifact never held fails even where the witness resolves.

## Scope

metric: what resolution establishes about a held passage
cohort: a Passages block and the pre-lift version its witness names
condition: an entry whose witness resolves

## Grounds

- code: src/claims_ledger/resolve.py § "resolve_passage" =sha256:9f82d15b344b24d21b8ff3431e2d6d0d00bb95cb1050db6361328452f7a2bbe9

## Warrant

A witness that resolves shows only that the section existed with those bytes, not that the prose on the entry came out of it. The passage must also be a contiguous run of the lines that version held. A held passage that resolves while saying something the artifact never said is the failure this mechanism exists to make impossible.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-16T23:55:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "resolve_passage" =sha256:c7d935a5e65d60a4166b889778edc094fdfdb41a621a83fa4fc9d29364a094e2
  note: re-read after the comparison was made over lines rather than characters. The claim is what it was and the section now keeps it more nearly: a substring test passed a passage cut in the middle of a line, which is prose the artifact never held in the sense this entry means. What the section still cannot see is a passage shorter than what was removed, and it now says so where a reader will find it.

- 2026-09-17T00:25:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "resolve_passage" =sha256:fbbdc77168627cf8898412af5fc5a6488d190767dd1e1006b30bbbd58f7f4c83
  note: re-read after the run search was moved back inside this section from a helper beside it. The fix-review gate measured what the helper cost: with the comparison in a section no entry pins, putting the defective substring test back moved no digest and all five checkers went on reporting nothing, so one test stood between the branch and the bug it was opened to fix. The claim is unchanged and the section now holds the whole of what keeps it.

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
- docs/SCHEMA.md · standing · cites-as-live
