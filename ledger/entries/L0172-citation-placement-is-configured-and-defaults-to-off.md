---
id: L0172-citation-placement-is-configured-and-defaults-to-off
kind: claim
stated: 2026-09-08T16:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 81e62781d7f1ae57c01e717505eb6d3d16811aab81314a97f7aae8c608d3b643
---

## Assertion

Whether a citation is held to the span its entry pins is a configured setting with three outcomes, and a project that says nothing is asked nothing.

## Scope

metric: whether the rule runs, and at what outcome, for a project that has not configured it
cohort: the citation-placement setting
condition: any project the package is pointed at

## Grounds

- code: src/claims_ledger/config.py § "PLACEMENT_OUTCOMES" @abb827e3cd4a443f4cc9e90f1db52a3d5c853622
- code: src/claims_ledger/config.py § "DEFAULT_CITATION_PLACEMENT" @abb827e3cd4a443f4cc9e90f1db52a3d5c853622
- code: src/claims_ledger/config.py § "from_table" @abb827e3cd4a443f4cc9e90f1db52a3d5c853622

## Warrant

PLACEMENT_OUTCOMES is the whole of what the setting may be and DEFAULT_CITATION_PLACEMENT beside it is off; from_table refuses any other value by name rather than reading it as off, so a project that meant to turn the rule on and mistyped the value is told rather than left with a checker that said nothing. Off by default because the rule is only worth running once a project's existing citations satisfy it: arriving on a ledger with fifty misplaced citations, it would report fifty sites at once, which is the rate at which a report teaches its readers to scroll past it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-14T19:21:54-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" @abb827e3cd4a443f4cc9e90f1db52a3d5c853622
  artifact: sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67
  note: propagated from a moved ground

- 2026-09-14T19:22:21-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67
  note: re-read after the commit that adds the `merge-renumber` key. The citation-placement check is untouched and still refuses a value outside the three outcomes; the new check sits after it and is written the same way, which is what this claim asks of the placement setting rather than of the section.
- 2026-09-14T20:21:10-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67
  artifact: sha256:222a65392276c0cc61e35fec1bfabd395dee5590c848b57d4303b30b4f3ec738
  note: propagated from a moved ground

- 2026-09-14T20:21:11-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:222a65392276c0cc61e35fec1bfabd395dee5590c848b57d4303b30b4f3ec738
  note: re-read after the commit that fixes what the pre-merge gate found. The section lost a verbatim duplicate of the merge-renumber check, which had been written into it twice; the citation-placement check is untouched and still refuses a value outside the three outcomes.

## References

- src/claims_ledger/config.py · standing · cites-as-live
- README.md · standing · cites-as-live
