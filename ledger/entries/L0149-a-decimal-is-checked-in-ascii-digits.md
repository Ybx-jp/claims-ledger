---
id: L0149-a-decimal-is-checked-in-ascii-digits
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d668772a799e318670c0f436e97ef2b78b12e2f525decc65cc5534aba1985bca
---

## Assertion

A decimal in the frontmatter is checked against ASCII digits rather than by attempting a conversion, so a value written in other digits or naming a non-number is refused.

## Scope

metric: which strings are accepted as a decimal
cohort: the credence of a prediction or a hypothesis
condition: the conversion function accepts more than the schema does

## Grounds

- code: src/claims_ledger/schema.py § "DECIMAL_RE" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

DECIMAL_RE admits an optional sign, ASCII digits, a decimal point and an exponent, and nothing else. The conversion function is wider than the schema in three ways that matter: it accepts any Unicode decimal digit, so a credence written in another numeral system would pass as an ordinary number a reader could not see; it accepts a name for a value that is not a number; and it accepts digit-grouping underscores. A credence is compared and reported, so a value that reads as one thing and computes as another is worse than a refusal.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
