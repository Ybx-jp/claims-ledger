---
id: U0002-footer-build-is-visible
kind: claim
stated: 2026-09-06T10:02:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0
---

## Assertion

The example footer renders the supplied build label.

## Scope

metric: presence of the build label in rendered footer text
cohort: Nimbus Console example builds
condition: any string supplied by the caller

## Grounds

- code: src/dashboard.ts § "renderFooter" @working

## Warrant

The current function interpolates its build argument into the returned footer. The
working-tree pin deliberately opts this low-risk illustrative claim out of drift checks.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts


## References

