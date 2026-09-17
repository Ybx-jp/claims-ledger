---
id: L0264-a-witness-is-not-a-ground
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 525ed2594e964db5fb219492c1c431ddd6b98827bf58731dda5ada1614cc8541
---

## Assertion

A passage witness is written on its own block rather than as a ground, so freshness does not read it and the rule holding a grade to its evidence does not count it.

## Scope

metric: where a passage witness is written in an entry
cohort: the Grounds section and the Passages section
condition: an entry of any grade that holds lifted prose

## Grounds

- code: src/claims_ledger/validate.py § "check_passages" =sha256:d5f014157752ac2713c2dfff7f166fa5ad7aeb00b2f7bc6af49e6480e056934c

## Warrant

A ground is a datum the Warrant uses; a witness is the provenance of prose the entry now holds, which is a different job. Written as a ground it would do two wrong things at once: flag forever under freshness, and hand an asserted entry an evidence ground that grade forbids.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
