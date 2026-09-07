---
id: B0001-service-and-ui-share-threshold
kind: claim
stated: 2026-09-06T10:05:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0
---

## Assertion

The service classifier and UI behavior contract agree on an inclusive risk threshold of
0.72.

## Scope

metric: decision boundary returned by the risk classifier
cohort: finite risk scores from zero through one
condition: default Nimbus policy

## Grounds

- code: service/risk.py § "classify_risk" @@BASE@
- source: ui-contract · banner rule

## Warrant

The pinned classifier uses the same inclusive comparison stated by the independently
versioned UI contract, establishing agreement at the repository boundary.

## Backing

- source: ui-contract · banner rule
  speaker: Nimbus Console maintainers
  quote: "The console displays a review banner when the API risk score is at least 0.72."

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

- README.md · standing · cites-as-live
