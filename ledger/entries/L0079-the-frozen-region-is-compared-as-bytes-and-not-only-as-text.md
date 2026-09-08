---
id: L0079-the-frozen-region-is-compared-as-bytes-and-not-only-as-text
kind: claim
stated: 2026-09-08T02:30:44-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 9a838d40dcfa89ba614d412e6825493b4bbbf3f1ad5b24976b7e188301010f43
---

## Assertion

The frozen region is compared as bytes as well as text, so a region rewritten from CRLF to LF fails even though it reads the same.

## Scope

metric: whether a line-ending rewrite of the frozen region is caught
cohort: committed entries under a repository
condition: every other comparison decodes both sides through universal newlines

## Grounds

- code: src/claims_ledger/validate.py § "_frozen_bytes" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

_frozen_bytes takes the region out of the raw blob and out of the file's raw bytes, and check_history compares those two when the text comparisons have found nothing. Every other comparison in the checker decodes both sides, which folds CRLF and LF onto each other: an entry whose frozen region was rewritten line for line matched itself as text while every byte of it had changed. Immutable is a statement about bytes, so the bytes are what settles it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
