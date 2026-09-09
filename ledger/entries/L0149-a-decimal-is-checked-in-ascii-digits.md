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

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "DECIMAL_RE" @4af0acd253eeef1571cd7615ea3a041eda9e945e
  artifact: 36052faf227379aac7e17f339c1c6b3937d1f6c1
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "DECIMAL_RE" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

## References

- src/claims_ledger/schema.py · standing · cites-as-live
