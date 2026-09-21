---
id: L0300-a-key-pattern-is-anchored-at-the-margin-in-both-directions
kind: claim
stated: 2026-09-20T17:56:18-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 04e7b7ff3d83fc498b12db6267be656747f40850328f42249f6dd1e44ef2cca8
---

## Assertion

Every section pattern this project publishes for a key or a declaration refuses a leading space or tab, so the pattern that finds a section's end is anchored at the left margin the same way the pattern that finds its start is.

## Scope

metric: whether a key's section runs to the end of its value or stops inside it
cohort: the `code` and `toml-key` patterns in this project's section-patterns table, and the copies of each in the documents that publish them
condition: the value is written across several lines and holds an indented `=`

## Grounds

- toml: pyproject.toml § "tool.claims-ledger.section-patterns" =sha256:cba2a5418154228b99b082d4121ad9e1b76f86cde076c12bb5c3462a963aa08a
- code: tests/test_section_scoping.py § "test_a_toml_key_section_runs_to_the_end_of_a_multi_line_value" =sha256:29f5127a0443c7152e6ce8e31a59b24defa974113618698fc248bb5c92aefc61
- code: tests/test_section_scoping.py § "test_the_documented_toml_key_recipe_is_the_same_string_in_every_place_it_is_written" =sha256:c506a2c77b913f5f6d79462ac4c4d5d8986816c56c5f2e606de05c9b972fd585

## Warrant

One pattern decides both ends of a section: the end is found by the same pattern with the name slot widened to `[^\n]+?`, and `[^\n]+?` matches leading whitespace. So an `^`-anchored pattern stops being anchored the moment it is widened, and the guard `(?![ \t])` is what puts the anchor back. `code` carried it and the comment above the table said why — the lookahead keeps an indented assignment from ending a function at its first local. `toml-key` had the same failure mode and no guard, which is issue #57; the table is the ground because the two patterns are one rule and a guard on only one of them is the defect.

Measured against this repository's own `pyproject.toml`, calling `section_span` directly with each pattern. `citation-slug`, seventeen lines of TOML, got five of them under the shipped pattern — its own line plus the four comment lines above the first element — and stopped at the indented `{ paths = [`. Under the guarded pattern it gets all seventeen. Every other key in the file is byte-identical either way: `documents`, a thirteen-line array of plain strings, already got its whole value, because the pattern finds no `=` inside it. Only a key whose value holds an indented `=` differs, which is why nothing in the ledger was wrong and the recipe still was.

The truncation was silent, and that is what makes it worth a claim rather than a fix. `resolve` and `freshness` both compare the span the pattern returns, so a ground pinned there resolved and stayed fresh while naming text that held none of the value it was about.

The third ground is the consistency check, and it is here because the recipe is published in three places and nothing held them together. `code` has had such a test over its four copies since it was written; `toml-key` had none, and the three copies could have been fixed one at a time with every gate green. Measured: with `README.md` left on the unguarded recipe and `pyproject.toml` on the guarded one, that check fails and so does the span test.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- pyproject.toml · standing · cites-as-live
