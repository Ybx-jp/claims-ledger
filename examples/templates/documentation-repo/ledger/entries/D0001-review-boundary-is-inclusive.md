---
id: D0001-review-boundary-is-inclusive
kind: claim
stated: 2026-09-06T10:10:00-07:00
author: main
grade: asserted
supersedes: none
verbatim_sha: 0
---

## Assertion

Nimbus sends risk scores at or above 0.72 to review.

## Scope

metric: documented review decision boundary
cohort: Nimbus API and Console contracts
condition: default example policy

## Grounds

- source: backend-contract · GET /claims/{id}/risk
- source: ui-contract · banner rule

## Warrant

Two independently versioned repository contracts state the same inclusive boundary; the
documentation therefore uses their shared wording without claiming a measurement.

## Backing

- source: backend-contract · GET /claims/{id}/risk
  speaker: Nimbus service maintainers
  quote: "description: Scores greater than or equal to 0.72 require review."
- source: ui-contract · banner rule
  speaker: Nimbus Console maintainers
  quote: "The console displays a review banner when the API risk score is at least 0.72."

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

- README.md · standing · cites-as-live
- docs/operator-guide.md · standing · cites-as-live
