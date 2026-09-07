---
id: U0001-ui-banner-uses-service-threshold
kind: claim
stated: 2026-09-06T10:00:00-07:00
author: main
grade: controlled
supersedes: none
verbatim_sha: 0
---

## Assertion

The Nimbus Console review banner uses the same 0.72 risk threshold exposed by the
backend service.

## Scope

metric: risk score boundary that selects the review banner
cohort: Nimbus Console risk summaries
condition: finite API score from zero through one

## Grounds

- code: src/dashboard.ts § "renderRiskBanner" @@BASE@
- source: backend-contract · GET /claims/{id}/risk

## Warrant

The pinned rendering branch and the API contract state the same inclusive boundary, so
requests at or above the service threshold select the review presentation.

## Backing

- source: backend-contract · GET /claims/{id}/risk
  speaker: Nimbus service maintainers
  quote: "description: Scores greater than or equal to 0.72 require review."

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

- README.md · standing · cites-as-live
