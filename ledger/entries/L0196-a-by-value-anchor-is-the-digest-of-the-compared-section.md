---
id: L0196-a-by-value-anchor-is-the-digest-of-the-compared-section
kind: claim
stated: 2026-09-10T21:48:10-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 48e178a7e07aeac7362921a75d56684e2272703765f1fbc96d1777f36c4c133f
---

## Assertion

An anchor stated by value is the sha256 of the section exactly as the freshness comparison reads it, decoded as UTF-8 through universal newlines with trailing whitespace stripped, so it sets no comment or formatting aside and can be computed from the working tree before any commit exists.

## Scope

metric: what text a by-value anchor digests
cohort: every evidence pointer written with an = anchor, in Grounds and in verdict evidence
condition: the section is found through the type's configured section pattern

## Grounds

- code: src/claims_ledger/schema.py § "section_digest" =sha256:838a8d521e361f620877e237ba705f7268eeeff471a78e79a370fb6ab44b23eb

## Warrant

section_digest takes the artifact text as read_artifact and git_call decode it, finds the section through section_text with the same pattern resolve and freshness use, and hands it to digest_of, which strips trailing whitespace and hashes the UTF-8 bytes with sha256. Nothing else is normalized: the comparison the checker makes is byte identity after that decode, and a digest over anything narrower would be a judgement about which edits matter, which the checkers refuse to make. Because the input is text in the tree rather than an object in history, the anchor exists before the commit that carries the entry does, which is what removes the two-commit landing shape.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/schema.py · standing · cites-as-live
