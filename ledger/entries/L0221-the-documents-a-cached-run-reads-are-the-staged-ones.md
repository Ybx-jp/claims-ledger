---
id: L0221-the-documents-a-cached-run-reads-are-the-staged-ones
kind: claim
stated: 2026-09-11T19:40:22-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 2cc0191e385be71bd139bf446f6464be7040f6671907a7760c5e5e10fd60dc7b
---

## Assertion

A reference check asked for the index reads each configured document from the index where the index holds it, so the citation held to a status is the one the commit will carry.

## Scope

metric: which tree the text of a configured document is read from under the cached flag
cohort: every reference check given the flag
condition: a document the index does not hold is read from the working tree, as before

## Grounds

- code: src/claims_ledger/schema.py § "staged_documents" =sha256:cef071ea4e70d5ca1d14410c69e8f90b13f9f463513418c6477cf429705dff29
- code: src/claims_ledger/references.py § "document_bodies" =sha256:1d3591af644202b102924d0dda4d82fedf80759f2e7c60b5d055bd13a359b078

## Warrant

A citation is prose, and the prose a commit carries is the prose in the index. This checker read the working tree whatever it was asked, so a citation staged against one status and corrected in the tree alone passed the hook and landed broken: the check reported on text no commit contains. Measured, with a note citing an id nothing minted staged and the citation corrected in the tree, the bare run exits 0 and the cached run exits 1 naming the id. A document the index does not hold falls back to the tree rather than being dropped, because a document that is not staged is not being changed by this commit and the tree's copy is what the commit leaves behind. The bodies are read once for the run and handed to the three loops that want them, where each used to read every document again.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- src/claims_ledger/references.py · standing · cites-as-live
