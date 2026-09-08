---
id: L0157-distinguishes-is-an-act-between-entries
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 49485f60bc2f7b68003b0fffdc116467b6217d1d7d96fc558d2d2d8b6695a86b
---

## Assertion

An entry may perform the distinguishes act on another entry and a document may not, because the pattern that reads a document is built from the citation acts alone.

## Scope

metric: which acts a ground may carry and which acts a document citation may carry
cohort: the act vocabulary as the package declares it
condition: the package as it ships

## Grounds

- code: src/claims_ledger/schema.py § "ENTRY_ACTS" @aadceb0aba82a85fe71b15394896c43977751709
- code: src/claims_ledger/schema.py § "CITATION_RE" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

ENTRY_ACTS is the citation acts plus distinguishes and is what validate holds a ground to; CITATION_RE is built by joining ACTS, which does not include it, so the act is unmatchable in a document by construction rather than by a rule somebody remembered to write. A document is not a claim and has no Scope, so there is nothing for it to hold apart from anything; giving it the act would let a sentence assert a difference between two claims that neither claim records.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
