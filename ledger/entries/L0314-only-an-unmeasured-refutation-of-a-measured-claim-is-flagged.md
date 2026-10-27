---
id: L0314-only-an-unmeasured-refutation-of-a-measured-claim-is-flagged
kind: claim
stated: 2026-10-27T11:35:47-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d27ef8494f93be64c217493a1ce8bd7c60d83a136e63b4c6f835051649723a71
---

## Assertion

A refuted verdict is flagged for review only when its grade is not a measurement and the entry it refutes is graded measured or above; a refutation at any other differing grade draws nothing.

## Scope

metric: whether validate flags a refuted verdict on the comparison of its grade with the entry's
cohort: refuted verdicts, at every pairing of entry grade and verdict grade
condition: measured, controlled and preregistered are the measurement grades the schema already requires an evidence ground for

## Grounds

- code: src/claims_ledger/validate.py § "check_verdicts" =sha256:89515a1cf788ae4277e45576763746557c7cdc50479c90c4bb9284a2ebe5b301
- code: tests/test_schema.py § "test_only_an_unmeasured_refutation_of_a_measured_claim_is_flagged" =sha256:bd1600355b957807047914ff78e405004d14a843340149c686d77dcce5fdf6cd

## Warrant

check_verdicts flags a refuted verdict when the entry's grade is in MEASURED_AND_ABOVE and the verdict's grade is a grade outside it, and on no other comparison of the two. Issue #83 measured the rule it replaced, which flagged every refutation at a grade other than the entry's: in a ledger that preregisters hypotheses at argued and settles them by measurement, all seven refuted hypotheses carried a flag no verdict could discharge, while the eleven corroborated the same way carried none. Grades are evidence types with no quality ranking, so a differing grade is not suspect for that alone; the line the schema does draw is whether the evidence is a measurement, and an argument against a measurement is the shape corpus seed D12 holds as a flag, because it is usually contested until a measurement exists. The test drives eight pairings through validate — measured refuted at argued and controlled at asserted flagged; argued refuted at measured and at preregistered, controlled at measured, measured at preregistered, argued at asserted and measured at measured not — and five of them were red against the rule it replaced.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- docs/SCHEMA.md · standing · cites-as-live
- src/claims_ledger/validate.py · standing · cites-as-live
