---
id: L0171-the-lookup-hands-over-the-line-it-would-take
kind: claim
stated: 2026-09-08T13:50:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: a35b11878c9fc7e262271a6403e3201450c59c12b3b9451d49db1a66e2864335
---

## Assertion

The lookup ends its answer with the ground line that would record a distinction, written out once for every pair it found no relation for.

## Scope

metric: whether the ground line that would record a distinction is written out, and for which pairs
cohort: the answer the neighbours lookup gives about one entry or one ground
condition: at least one neighbour with no relation recorded

## Grounds

- code: src/claims_ledger/neighbours.py § "handover" @989493fa4655725014cedb6408b4ff9c7e680498
- code: src/claims_ledger/neighbours.py § "run" @989493fa4655725014cedb6408b4ff9c7e680498

## Warrant

handover builds one pointer line per unrelated neighbour and run appends what it built, so a pair the lookup reported as already related draws no line and a pair it did not draws exactly one. The line is the last thing this command can produce without deciding anything: it is the same text whichever neighbour it names, so writing it out asserts nothing about which of them deserves it, while composing it from memory costs the reader the pointer syntax, the act, and which of the two entries may carry the ground. The caveat travels with it, because Grounds are frozen and the line is only writable into an entry that is not yet committed.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:17:14-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/neighbours.py § "run" @989493fa4655725014cedb6408b4ff9c7e680498
  artifact: d97c5dd2d2bf791df9ac91d3bf84227f624339a8
  note: propagated from a moved ground

- 2026-09-08T14:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/neighbours.py § "run" @ee234ed85969dcc0c8400721f9a16162d6cee9f5
  note: read against commit ee234ed: the citing comment moved into this section from outside it, so the section now carries the sentence it always managed; run still appends what handover built and builds no Report

## References

- src/claims_ledger/neighbours.py · standing · cites-as-live
- README.md · standing · cites-as-live
