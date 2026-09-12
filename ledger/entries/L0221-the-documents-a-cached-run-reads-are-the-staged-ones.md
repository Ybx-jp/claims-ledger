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

- 2026-09-11T22:04:31-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "staged_documents" =sha256:4b689b4467db42f58ddd5b1413c27c5d60f8d751f20f9775b441b4333cc4372d
  note: re-read after the commit answering the fix-review gate on this branch (qe ticket e9b7d35601214a1b). This now returns (text, problem) in the shape `read_document` returns, decodes strictly, and keeps a path git could not answer for rather than dropping it. Which documents are read from the index is unchanged.

- 2026-09-11T22:04:31-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/references.py § "document_bodies" =sha256:d7b05530f9ea7a17716bd87da386361e2f2e482be7a89acb4fccd8be69d58554
  note: re-read after the commit answering the fix-review gate on this branch (qe ticket e9b7d35601214a1b). The staged pair is taken as it comes rather than rewrapped, so a staged document that is not UTF-8 and one git could not be asked about are both reported. Reading each document once for the run, from the index under the flag, is unchanged.

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- src/claims_ledger/references.py · standing · cites-as-live
