---
id: L0281-the-documented-recipe-starts-a-section-at-the-prefix
kind: claim
stated: 2026-09-20T11:36:09-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: f7dc85d2ce9e3c417b464a67a683a6ff9b7087130f9a89740421ad2bf792dfc9
---

## Assertion

The `code` recipe the package documents starts a section at the run of decorators above a definition, so a prefixed declaration and its prefix are one section.

## Scope

metric: where a section of a Python artifact begins under the documented recipe
cohort: top-level definitions and assignments, decorated and undecorated
condition: the pattern is the one README, docs/OPERATING.md, the skill and init write

## Grounds

- code: tests/test_section_scoping.py § "test_the_documented_recipe_puts_a_prefix_with_the_declaration_it_belongs_to" =sha256:9dc5df112c0facd7abcd88f58cce278a3fd5e5d4e1fcbf69bc3f09dc6940ed1f

## Warrant

The test reads the recipe out of the files that document it rather than restating it, and drives both halves of the boundary at once: the section above a decorator ends before it, and the decorated definition's section starts at it. Undecorated definitions and plain and annotated assignments are driven in the same table, so a recipe that fixed the prefix by losing them fails here. Measured over this repository's own ledger the day it was adopted: 391 `code:` grounds, 382 of them resolvable in the working tree, and the recipe resolves all 382, leaves 376 spans byte-identical and moves 6 onto the declaration the prefix belongs to. This repository has not switched to it; the 6 are what switching would cost, one re-read verdict each.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- docs/OPERATING.md · standing · cites-as-live
