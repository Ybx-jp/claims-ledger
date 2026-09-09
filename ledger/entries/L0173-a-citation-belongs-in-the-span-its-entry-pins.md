---
id: L0173-a-citation-belongs-in-the-span-its-entry-pins
kind: claim
stated: 2026-09-08T16:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 65d645f55662445f96980f80dde60faa0688f04b6abd50d2fe95423e22bf4779
---

## Assertion

A citation is reported when the entry it names rests on a section of that same document and the citation sits outside every such section.

## Scope

metric: which citations are reported for their placement, and which are passed over
cohort: citations in a document the cited entry also rests on by a sectioned ground
condition: the project has configured the rule on

## Grounds

- code: src/claims_ledger/references.py § "misplaced_citations" @abb827e3cd4a443f4cc9e90f1db52a3d5c853622

## Warrant

misplaced_citations collects the sections of this document that the cited entry's sectioned grounds name, passes over the citation when there are none, and reports only when the citation's offset is inside none of them. Both halves of that are the rule: a claim resting on several sections of one file is satisfied from any of them, and a citation of an entry grounded elsewhere is asked nothing, because there is no span in this file for it to be outside of. What the rule buys is that the sentence stating a commitment and the span keeping it are one section, so an edit reaches both and a reader who finds either finds the other.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/references.py · standing · cites-as-live
