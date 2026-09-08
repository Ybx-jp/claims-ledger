---
id: L0159-a-citation-shaped-parenthetical-names-a-citation-act
kind: claim
stated: 2026-09-08T12:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 7451efaa7bdf0a214f19269d67e716fe39fc1432b6cdf7039a0f8d06eda39ead
---

## Assertion

A parenthesis in a document holding an entry id, a comma and an act-shaped word is reported when that word is not a citation act, rather than passing as prose.

## Scope

metric: whether a citation-shaped parenthesis with an illegal act is reported
cohort: every document the configuration reaches
condition: the word after the comma is lowercase letters and hyphens and is not one of the citation acts

## Grounds

- code: src/claims_ledger/schema.py § "MISCITATION_RE" @aadceb0aba82a85fe71b15394896c43977751709
- code: src/claims_ledger/references.py § "run" @aadceb0aba82a85fe71b15394896c43977751709

## Warrant

CITATION_RE is built from the citation acts, so a mistyped act matches nothing and no other rule reads documents: before this the sentence sat in a checked document as text nothing looked at, which is the one report this package must never withhold. MISCITATION_RE matches the same shape with any act-shaped word and run reports every match the citation acts do not cover. The rule is narrow on purpose: an id in a parenthesis of its own, or in running prose, is a document naming an entry rather than citing it, and is left alone.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:17:13-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "MISCITATION_RE" @aadceb0aba82a85fe71b15394896c43977751709
  artifact: c5b5dfd25c552c75745d3195f6b7e593a401b19e
  note: propagated from a moved ground

- 2026-09-08T14:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "MISCITATION_RE" @ee234ed85969dcc0c8400721f9a16162d6cee9f5
  note: read against commit ee234ed: the citing comment moved into this section from outside it, so the section now carries the sentence it always managed; the pattern is unchanged
- 2026-09-08T14:43:44-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/references.py § "run" @aadceb0aba82a85fe71b15394896c43977751709
  artifact: f9db731e0b23468e3e0628c6ac6c35712cd7310d
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/references.py § "run" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- src/claims_ledger/references.py · standing · cites-as-live
