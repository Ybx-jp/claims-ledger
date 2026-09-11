---
id: L0197-a-pending-anchor-is-refused-until-it-is-computed
kind: claim
stated: 2026-09-10T21:48:10-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: a43581926af768eb7ca50103b856b093e5b4d51b74902730a9ffc9409d497e15
---

## Assertion

A by-value anchor left as the placeholder is refused by validate, of every evidence pointer in the Grounds and in verdict evidence, before any artifact is read.

## Scope

metric: whether an entry carrying an = anchor that is the placeholder or not a digest passes validate
cohort: every evidence pointer written with an = anchor, in Grounds and in verdict evidence
condition: validate runs on the entry, committed or not

## Grounds

- code: src/claims_ledger/validate.py § "check_anchors" =sha256:d8b561f455671f252359098d9f4049adc70692c944b75c3b8b943e5576d67f7c

## Warrant

check_anchors walks the Grounds and every verdict's evidence, and for each evidence pointer whose anchor is stated by value fails the entry when the digest is the placeholder or is not sha256 over 64 hex characters. The placeholder is what sha --write fills; a ground left with it names no datum, so no later checker could compare it against anything, and refusing it where the shape is checked keeps that from being discovered downstream as a comparison that quietly matched nothing.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/validate.py · standing · cites-as-live
