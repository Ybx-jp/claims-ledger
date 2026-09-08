---
id: L0165-a-recorded-relation-is-named-so-it-is-not-drawn-twice
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 684e9ce8844f56dab889c310aeae7ad90702dff01c7c5d7835a45bba85e80ae5
---

## Assertion

Each neighbour is answered with the relation the ledger already records between the two entries, and a pair the ledger records nothing about is ordered ahead of one it does.

## Scope

metric: whether an existing relation between two entries is named in the result, and where the pair is ordered
cohort: neighbours proposed for one subject entry
condition: an entry ground either way, or a supersession either way

## Grounds

- code: src/claims_ledger/neighbours.py § "relation" @aadceb0aba82a85fe71b15394896c43977751709
- code: src/claims_ledger/neighbours.py § "find" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

relation reads the grounds of both entries for an entry pointer at the other and the supersedes field of each, which is every link between two entries the checkers can already see, and find sorts on whether relation answered before it sorts on anything else. The lookup exists to surface the pair nobody has read together; a pair somebody has already reconciled, superseded or distinguished is not that pair, and proposing it again is how a lookup becomes noise. Grounds are frozen once committed, so the newer entry is the only one that can record the relation, and this is what reads it from the other side.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:17:13-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/neighbours.py § "find" @aadceb0aba82a85fe71b15394896c43977751709
  artifact: d97c5dd2d2bf791df9ac91d3bf84227f624339a8
  note: propagated from a moved ground

- 2026-09-08T14:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/neighbours.py § "find" @ee234ed85969dcc0c8400721f9a16162d6cee9f5
  note: read against commit ee234ed, which moved a citing comment into find's docstring; the sort that puts unrelated pairs first is unchanged

## References

- src/claims_ledger/neighbours.py · standing · cites-as-live
