---
id: L0044-a-citation-and-its-references-row-must-agree
kind: claim
stated: 2026-09-08T02:08:33-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: aa50d521109f632c90ee37209174147d03c9e5bdb225bbea406ee2de52b84fe9
---

## Assertion

A document citing an entry fails unless that entry's References section lists the document with the same act, and a References row fails unless the document it names really cites the entry that way.

## Scope

metric: whether each side of the document-to-entry correspondence is checked against the other
cohort: inline citations in configured documents, and References rows in entries
condition: the document is readable and among the configured documents

## Grounds

- code: src/claims_ledger/references.py § "run" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487

## Warrant

run builds, per document, the set of id-and-act pairs it actually found, and checks the correspondence twice against that same set: a citation whose target lists no matching row fails as the citation is read, and afterwards every References row is looked up in the set recorded for the document it names. A row naming a document the checker cannot see is reported as that rather than as a mismatch, so a configuration gap and a wrong act are told apart in the report.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/references.py · standing · cites-as-live
