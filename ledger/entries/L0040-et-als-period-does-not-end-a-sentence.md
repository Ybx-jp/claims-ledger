---
id: L0040-et-als-period-does-not-end-a-sentence
kind: claim
stated: 2026-09-08T02:02:28-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 13f3266d8c64b093f5167889edca151469cb279eab9da7c5a0cb82ed69357d18
---

## Assertion

The period of the abbreviation et al. is not read as a sentence end when a span is widened to the sentence containing it.

## Scope

metric: whether a sentence boundary is recorded at the period of the abbreviation
cohort: source text containing et al.
condition: sentence bounds are being computed for the relayed-material flag

## Grounds

- code: src/claims_ledger/resolve.py § "sentence_bounds" @ec82c16045421ce5a6cb71befe8ddbe6067489ae

## Warrant

sentence_bounds skips a period whose preceding characters are et al, so the window continues past the abbreviation. Stopping there would end the sentence immediately before the citation the abbreviation introduces, and the flag that looks for relayed authority would search a window from which that authority had just been cut.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
