---
id: L0263-a-witness-is-stated-by-value-so-freshness-never-reads-it
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 3f84556bd41ac35b28cf157c06a593ef6ef63172783a0106198a29d93dfb7952
---

## Assertion

A passage witness is stated by value and a witness stated by reference is refused, because freshness compares every pinned evidence pointer against the tree and a witness names text the tree no longer holds.

## Scope

metric: the anchor form a passage witness may take
cohort: the lifted line of a Passages block
condition: a witness for prose the lift has already removed

## Grounds

- code: src/claims_ledger/validate.py § "check_passages" =sha256:d5f014157752ac2713c2dfff7f166fa5ad7aeb00b2f7bc6af49e6480e056934c

## Warrant

The pointers freshness checks are the evidence pointers carrying a real pin. A witness written at a commit would therefore be read against the working tree on every run and reported moved for the rest of the ledger's life, and no verdict could discharge it, because the finding would be true. Stated by value there is no pin for that comparison to find.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
- docs/SCHEMA.md · standing · cites-as-live
