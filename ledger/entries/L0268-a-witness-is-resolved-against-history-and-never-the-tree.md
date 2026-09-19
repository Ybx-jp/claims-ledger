---
id: L0268-a-witness-is-resolved-against-history-and-never-the-tree
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: e2faf8541859478b87c2a4c120869b492689304c7fb2b354c806ad45cf2cf1bf
---

## Assertion

A passage witness is resolved against the history alone, never against the working tree.

## Scope

metric: where a witness is looked for
cohort: the resolution of a Passages block
condition: a lift that has already removed the prose

## Grounds

- code: src/claims_ledger/resolve.py § "resolve_passage" =sha256:9f82d15b344b24d21b8ff3431e2d6d0d00bb95cb1050db6361328452f7a2bbe9

## Warrant

The lift removed the prose, so the tree cannot hold the pre-lift section by construction. Asking the tree first would report a failure on every run for a passage that is perfectly well witnessed, and would make the one-commit shape impossible: the history holds the pre-lift blob the moment the lift is planned.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-16T23:55:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "resolve_passage" =sha256:c7d935a5e65d60a4166b889778edc094fdfdb41a621a83fa4fc9d29364a094e2
  note: re-read after the same edit. It changed what the second proposition compares and nothing about where the first one looks: `digest_in_history` is still the only call, and the tree is still not asked.

- 2026-09-17T00:25:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "resolve_passage" =sha256:fbbdc77168627cf8898412af5fc5a6488d190767dd1e1006b30bbbd58f7f4c83
  note: re-read after the same move. Where the witness is looked for did not change: `digest_in_history` is still the only call and the tree is still not asked.

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
- docs/SCHEMA.md · standing · cites-as-live
