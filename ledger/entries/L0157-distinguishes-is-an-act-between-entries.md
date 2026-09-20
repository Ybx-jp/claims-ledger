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

- 2026-09-08T14:17:13-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "ENTRY_ACTS" @aadceb0aba82a85fe71b15394896c43977751709
  artifact: c5b5dfd25c552c75745d3195f6b7e593a401b19e
  note: propagated from a moved ground

- 2026-09-08T14:17:13-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "CITATION_RE" @aadceb0aba82a85fe71b15394896c43977751709
  artifact: c5b5dfd25c552c75745d3195f6b7e593a401b19e
  note: propagated from a moved ground

- 2026-09-08T14:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "ENTRY_ACTS" @ee234ed85969dcc0c8400721f9a16162d6cee9f5
  note: read against commit ee234ed: the citing comment moved into this section from outside it, so the section now carries the sentence it always managed; the tuple is the citation acts plus distinguishes, as before

- 2026-09-08T14:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "CITATION_RE" @ee234ed85969dcc0c8400721f9a16162d6cee9f5
  note: read against commit ee234ed, which moved the comment above MISCITATION_RE below it and so out of this section; the pattern is still built by joining ACTS and so still cannot match the act
- 2026-09-20T10:46:49-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "CITATION_RE" @ee234ed85969dcc0c8400721f9a16162d6cee9f5
  artifact: sha256:2b42a3fc5cbf3e14892515516ce6eea36249e1425001c84cd77928d08e8b13d9
  note: propagated from a moved ground

- 2026-09-20T10:47:03-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "CITATION_RE" =sha256:2b42a3fc5cbf3e14892515516ce6eea36249e1425001c84cd77928d08e8b13d9
  note: read against the commit that writes a citing comment into this section, for the claim that a citation is read wherever a document's text holds it; the pattern is still built by joining ACTS, so distinguishes is still not a word any document may cite with

## References

- src/claims_ledger/schema.py · standing · cites-as-live
