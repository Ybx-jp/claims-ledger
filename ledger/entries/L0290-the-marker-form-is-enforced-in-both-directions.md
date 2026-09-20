---
id: L0290-the-marker-form-is-enforced-in-both-directions
kind: claim
stated: 2026-09-20T13:30:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d916faf6e455b4858155486ace6206c14f415eedc2a8d03d8a80e177d9209e79
---

## Assertion

Every citation marker in this repository is held to a spelling: the id alone in the three files named as converted, and the whole id in every other document.

## Scope

metric: whether a marker written in the other spelling is reported
cohort: the markers in this repository's configured documents
condition: the document is one of the three named, or is any other

## Grounds

- toml: pyproject.toml § "tool.claims-ledger" =sha256:5d20c70ea19910c494d512523f97210ac78a22469afa7ffa8ac88ac4990495bd
- entry: L0286-a-path-rule-is-the-first-one-that-matches · cites-as-live

## Warrant

The setting is a list of two rules and the earliest match decides, so naming the three converted files above a catch-all makes the catch-all mean every document except those. Both halves are load-bearing and the second is the one a project would leave out: without it a converted marker could be written back in the long form, or an unconverted one shortened, and neither would be reported — the migration would be a convention rather than a rule, and a convention is what the checkers exist to replace. Measured over the working tree on 2026-09-20: 423 markers, 7 short in the named files and 416 long elsewhere, all five checkers clean; putting the slug back into one of the three and taking it off one marker in docs/OPERATING.md produced one failure each, naming the spelling that document wants and the id in it.

The ground is the table and not the key, which is the narrower pointer and was tried first. A toml-key section runs from its own line to the next line the same pattern matches, and that pattern ends a section at any line carrying a space-padded equals sign — including the `{ paths = [` of an inline table one indent in. So this key's section is its own first line and nothing after it: a span that holds none of the rules, that no edit to them can move, and that the citation sits outside of. citation-placement is fail here, so references named that rather than leaving a ground which could never go stale. The table is the finest pointer that actually contains the value, and the cost is the documented one — it moves when any other key in it moves.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-20T13:56:34-07:00 · superseded · grade: measured · author: main
  evidence: entry: L0291-the-marker-form-is-enforced-in-both-directions · supersedes
  note: the Assertion, Scope, Grounds and Backing are carried across unchanged, and the fingerprint is byte-identical, so nothing about the claim moved. What moved is a sentence of the Warrant that was false: it said the section of the citation-slug key is the key's own line and nothing after it. Measured, it is five lines and 312 characters — the key's line and the comment above the first rule. The conclusion drawn from it stands, since none of those five lines holds a rule, but a Warrant is not compared against anything by any checker, so the only repair for a wrong one is a successor. The commit that introduced it, e2d4947, carries the same sentence in its message and is not rewritten for it.


## References
