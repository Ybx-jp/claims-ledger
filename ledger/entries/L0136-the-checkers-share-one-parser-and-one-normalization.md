---
id: L0136-the-checkers-share-one-parser-and-one-normalization
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6cf2f7627a7f0ab7fb2348a3a20933166a7bda759c02b3a16157ffa3117a23d6
---

## Assertion

The four checkers read an entry through one parser, one normalization, one fingerprint and one status derivation, so two of them cannot disagree about what an entry says.

## Scope

metric: the number of definitions in the package that parse an entry, normalize text, compute the fingerprint, or derive a status
cohort: validate, resolve, references and propagate
condition: the package as it ships

## Grounds

- code: src/claims_ledger/schema.py § "parse_entry" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "normalize" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "fingerprint" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "derive_status" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

Each of those four is defined once here and imported by the checkers rather than reimplemented in any of them. A second normalization would let the fingerprint and the resolver disagree about what counts as a change; a second status derivation would let one checker call an entry open while another called it contested, and every citation rule is written against the status. Sharing them makes disagreement between the checkers a thing that has to be introduced rather than a thing that has to be prevented.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
