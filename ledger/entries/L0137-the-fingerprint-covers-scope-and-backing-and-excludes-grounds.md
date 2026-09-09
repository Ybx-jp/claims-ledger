---
id: L0137-the-fingerprint-covers-scope-and-backing-and-excludes-grounds
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 99ba8f67321afe27be340e6c6635ba52ef0d28071c67c65e24854bda8f02483a
---

## Assertion

The verbatim fingerprint is computed over the Scope lines and the Backing blocks, with the blocks sorted, and excludes the Grounds entirely.

## Scope

metric: which sections of an entry the fingerprint covers
cohort: every entry
condition: reordering Backing blocks is expected to leave the value unchanged

## Grounds

- code: src/claims_ledger/schema.py § "fingerprint" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

fingerprint normalizes the Scope lines, then one sorted line per Backing block, and hashes the two together. Grounds are left out because they are the evidence, and evidence is exactly what a supersession is allowed to replace: a successor resting the same claim on a different artifact should carry the same verbatim record. Scope and Backing are what the claim was measured over and the words it rests on, so a successor changing either is stating something else — which is why validate requires a declared reason when they differ across a chain. Sorting the blocks makes reordering Backing a rearrangement rather than a rewrite.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
