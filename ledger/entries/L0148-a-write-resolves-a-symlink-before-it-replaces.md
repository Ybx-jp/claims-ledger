---
id: L0148-a-write-resolves-a-symlink-before-it-replaces
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 3c215ab870b589fd9dfae2760c84b161f6f0ae3267884747109866e412087368
---

## Assertion

A write resolves a symlink at its destination before replacing, so a ledger that reaches an entry through a link keeps one copy of it.

## Scope

metric: whether an atomic replace can turn a link into a second file
cohort: write targets reached through a symlink
condition: the containment question is asked separately by the caller

## Grounds

- code: src/claims_ledger/schema.py § "write_bytes_atomically" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

write_bytes_atomically resolves the path and replaces what the link points at. Replacing the link itself would leave the original file where it was and put a new one under the link's name, which for an entry reached through a link is two entries with one id — the parser would load both and every rule about a single entry would be applied twice. Where the link leads is a different question, and the callers ask it through the confinement test rather than here.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
