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

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- src/claims_ledger/references.py · standing · cites-as-live
