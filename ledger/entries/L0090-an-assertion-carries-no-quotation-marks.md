---
id: L0090-an-assertion-carries-no-quotation-marks
kind: claim
stated: 2026-09-08T02:30:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 879efc264a7357e5b313344eb121a089846ae18ddd2811e56e0253af999c4c42
---

## Assertion

An Assertion containing a quotation mark fails: source words live in Backing, where they are checked against the source that supplied them.

## Scope

metric: whether a quotation mark in an Assertion is reported
cohort: the Assertion of every entry
condition: straight and typographic marks alike

## Grounds

- code: src/claims_ledger/validate.py § "check_sections" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_sections tests the Assertion against both straight and typographic quotation marks and fails on any of them. A quotation in the Assertion wears the authority of a source while resolving to nothing: the resolver checks Backing spans against the bytes of the source that supplied them, and an Assertion is never read that way. Moving the words down to Backing is what makes them checkable at all.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
