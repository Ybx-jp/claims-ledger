---
id: L0034-a-sections-presence-is-checked-at-the-pin
kind: claim
stated: 2026-09-08T02:02:28-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 489965abaca4a4745533f90054d32772ec5c027fdbe505317d651aeadc72f4b6
---

## Assertion

A pointer that names a section of an artifact fails unless that section is found in the artifact's text as read at the pointer's own pin.

## Scope

metric: whether a sectioned pointer resolves when the section is absent from the pinned revision
cohort: grounds and verdict evidence naming a section
condition: the artifact itself resolves at the pin

## Grounds

- code: src/claims_ledger/resolve.py § "resolve_pointer" @ec82c16045421ce5a6cb71befe8ddbe6067489ae

## Warrant

Once the text is in hand — out of git at the pin, or off the working tree when the pin names no revision — resolve_pointer asks section_span for the named section in that same text and fails when the answer is absent. The question is put to the revision the ground pins rather than to the file as it stands now, so a ground whose section was never there at its pin is caught rather than read as satisfied.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
