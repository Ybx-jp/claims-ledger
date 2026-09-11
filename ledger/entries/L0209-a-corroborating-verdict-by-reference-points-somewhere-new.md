---
id: L0209-a-corroborating-verdict-by-reference-points-somewhere-new
kind: claim
stated: 2026-09-11T03:57:02-07:00
author: main
grade: measured
supersedes: L0094-a-corroborating-verdict-points-somewhere-new
verbatim_change: condition gains the anchor-form exemption; Backing unchanged
verbatim_sha: 7746f787d70bacb20f45362ca82093bd357fd10fa9c271b0f8626642653f62f3
---

## Assertion

A corroborating verdict stated by reference is refused when its evidence names a ground the entry already cites, and one stated by value may name the ground's own digest.

## Scope

metric: whether a corroborating verdict restating an existing ground is reported
cohort: verdicts with status corroborated
condition: the comparison is on the normalized pointer text, and the exemption on the anchor's form

## Grounds

- code: src/claims_ledger/validate.py § "check_verdicts" =sha256:2cc50a11f18089b10ca35b6968d534962c348565f1c4911bc74d46621f6af10b

## Warrant

check_verdicts normalizes the entry's grounds and the verdict's evidence, and on a match fails the verdict unless its pointer's anchor is stated by value. A corroboration asserts that somebody went and looked; a pointer at a commit the ground already names records no looking at all, which is what makes the verdict the record of a reading rather than a restatement. A digest is different: a reading that names the ground's own digest says the section was read again and found as the ground states it, which is the one reading that can move a record of a drift that was undone past, since the section as it now stands digests to nothing else.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/validate.py · standing · cites-as-live
