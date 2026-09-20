---
id: L0280-a-section-pattern-is-matched-over-the-whole-artifact
kind: claim
stated: 2026-09-20T11:32:24-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 50b6d9ac752c3075b72f2f1243bc9969fa831d3e1994f8ab4eee2c243bdf82fd
---

## Assertion

A configured section pattern is compiled with re.MULTILINE and matched over the whole artifact, so a pattern may span lines and a section may begin above the line that names it.

## Scope

metric: how a configured section pattern is matched against an artifact
cohort: every sectioned pointer of a type carrying a pattern
condition: the pattern is asked both where a section starts and where the next one does

## Grounds

- code: src/claims_ledger/schema.py § "section_header_re" =sha256:b29cdffb502a8c31c95d70901a89502e267ec4ebffb59492247d15d0b86ccfa3

## Warrant

section_header_re passes re.MULTILINE to re.compile, and section_span runs the result over the artifact's whole text and searches for the next header from the end of the match it found, so a header made of several lines consumes its own lines instead of re-matching inside them. A pattern may therefore carry the prefix a language puts in front of a declaration. The documentation said the opposite until 2026-09-20 — "an ordinary regex, matched line by line" — and that sentence, not the code, is what ruled out a decorator-aware pattern from the day section patterns shipped. Measured over this repository's 391 code grounds, of which 382 resolve in the working tree: the recipe the documentation now ships resolves all 382, leaves 376 spans byte-identical, and moves 6 onto the declaration the prefix belongs to.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- README.md · standing · cites-as-live
- docs/OPERATING.md · standing · cites-as-live
