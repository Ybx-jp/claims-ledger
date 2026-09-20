---
id: L0291-the-marker-form-is-enforced-in-both-directions
kind: claim
stated: 2026-09-20T13:55:58-07:00
author: main
grade: measured
supersedes: L0290-the-marker-form-is-enforced-in-both-directions
verbatim_sha: d916faf6e455b4858155486ace6206c14f415eedc2a8d03d8a80e177d9209e79
---

## Assertion

Every citation marker in this repository is held to a spelling: the id alone in the three files named as converted, and the whole id in every other document.

## Scope

metric: whether a marker written in the other spelling is reported
cohort: the markers in this repository's configured documents
condition: the document is one of the three named, or is any other

## Grounds

- toml: pyproject.toml § "tool.claims-ledger" =sha256:5c270f590d853be205d823df67a99804e2b68ba0fb614b83194181de68222e7b
- entry: L0286-a-path-rule-is-the-first-one-that-matches · cites-as-live

## Warrant

The setting is a list of two rules and the earliest match decides, so naming the three converted files above a catch-all makes the catch-all mean every document except those. Both halves are load-bearing and the second is the one a project would leave out: without it a converted marker could be written back in the long form, or an unconverted one shortened, and neither would be reported — the migration would be a convention rather than a rule, and a convention is what the checkers exist to replace. Measured over the working tree on 2026-09-20: 423 markers, 7 short in the named files and 416 long elsewhere, all five checkers clean; putting the slug back into one of the three and taking it off one marker in docs/OPERATING.md produced one failure each, naming the spelling that document wants and the id in it.

The ground is the table and not the key, which is the narrower pointer and was tried first. A toml-key section runs from its own line to the next line the same pattern matches, and that pattern ends a section at any line carrying a space-padded equals sign — including the indented opening of an inline table. So the section of this key stops at the first rule rather than running to the end of the value: measured, five lines and 312 characters, holding the key's own line and the comment above the first rule and none of the rules themselves. It is a span no edit to a rule can move, and one the citation sits outside of. citation-placement is fail here, so references named that rather than leaving a ground which could never go stale. The table is the finest pointer that actually contains the value, and the cost is the documented one — it moves when any other key in it moves.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- pyproject.toml · standing · cites-as-live
- CLAUDE.md · standing · cites-as-live
