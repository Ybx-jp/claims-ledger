---
id: L0139-a-nested-heading-is-part-of-the-section-above-it
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 13b661e9001ac462adf45d49fbb8226bcdc5e40a2f3f793ed5f1d3c8ba8f36ce
---

## Assertion

A heading nested under a section is part of that section rather than the start of the next one, for any pattern that says how its own depth is written.

## Scope

metric: whether a deeper heading ends the section above it
cohort: sectioned artifacts whose pattern carries a depth group
condition: a pattern without a depth group is flat, and every match ends the section

## Grounds

- code: src/claims_ledger/schema.py § "section_span" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

section_span reads the depth of the opening header and of each candidate end, and treats a longer depth as a subsection to walk past. A default that could not say this would leave every subsection of a pinned section outside the comparison, which is the quiet half of a section pin: the ground would go on reporting fresh while the material under it changed. A flat pattern says so by carrying no depth group, and then every match ends the section, which is what a flat pattern wants.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
