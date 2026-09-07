---
id: D0002-review-response-is-documented
kind: claim
stated: 2026-09-06T10:15:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0
---

## Assertion

The operator runbook requires a human verdict after evidence review and warns against
treating a clean mechanical check as truth.

## Scope

metric: presence of both operator instructions
cohort: example review runbook
condition: runbook version pinned by this entry

## Grounds

- run: runbooks/review.md @@BASE@
- source: research-summary · disclaimer

## Warrant

The pinned runbook contains both instructions, while the research disclaimer demonstrates
why the boundary between mechanical validity and truth matters in this portfolio.

## Backing

- source: research-summary · disclaimer
  speaker: Nimbus research maintainers
  quote: "These numbers are demonstration data, not empirical findings."

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

- README.md · standing · cites-as-live
- docs/operator-guide.md · standing · cites-as-live
