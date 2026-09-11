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

- 2026-09-10T21:49:35-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" @ec82c16045421ce5a6cb71befe8ddbe6067489ae
  artifact: 380802d3237b2e0a79b628ddda818b883cf042b5
  note: propagated from a moved ground
- 2026-09-10T21:49:48-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" =sha256:f01906eb76fb139642ae98df2065ca95a93dceb22e3ed5ee178f036c9203d30b
  note: read against the working tree after the anchor-by-value branch was added: a section is still checked for presence in the text read at the pointer's pin; a pointer anchored by value names no pin and is read from the tree instead, which narrows the cohort this states to pointers by reference and leaves the assertion true of them.
- 2026-09-11T02:49:32-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" =sha256:f01906eb76fb139642ae98df2065ca95a93dceb22e3ed5ee178f036c9203d30b
  artifact: sha256:55d28960d1b04ffe2db203a3b19334115b161628741178ffc4ed4882dac5893d
  note: propagated from a moved ground
- 2026-09-11T02:49:51-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/resolve.py § "resolve_pointer" =sha256:55d28960d1b04ffe2db203a3b19334115b161628741178ffc4ed4882dac5893d
  note: read against the working tree after the by-value branch was moved out of resolve_pointer into resolve_by_value: what remains is the unpinned read from the tree, the pinned read out of git, and the entry and source branches, and the failure messages now write the pin as @<pin> since no by-value anchor reaches them; the assertion holds as written.

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
