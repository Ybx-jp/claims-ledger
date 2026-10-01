---
id: L0313-the-pin-guard-is-silent-only-on-a-zero-count
kind: claim
stated: 2026-10-01T00:54:12-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 451ab8d526cd3549fbad7f70504b5f50d1a6a57f5b6f8be2e5f032b5df009ae6
---

## Assertion

The pin guard stays silent only on a freshness report whose failures and flags are both zero, and reports drift at any other count.

## Scope

metric: whether the pin guard reports drift on a freshness summary
cohort: summaries of the form `freshness (N entries): F failure(s), G flag(s)` for F and G of one or more digits
condition: the guard reads the summary `freshness` prints as the last line of its report

## Grounds

- code: tests/test_harness.py § "test_the_pin_guard_reads_the_whole_count_and_not_a_substring_of_it" =sha256:7df49e1651a4afd5652f3de7e3bf8d99b42a35f01d3d5b51aed8e318fcb091d6

## Warrant

The guard asked whether the report contained `0 failure(s), 0 flag(s)` anywhere, and `10 failure(s), 0 flag(s)` contains it, so ten failures read as clean: the `qe` fix-review round (ticket `1333d78c3857456e`) measured the guard silent on 10 and 20 failures and speaking on 9. The guard now reads the count from the colon to the end of the line. The test hands it, through a stand-in interpreter, a zero summary and asserts silence, then 10 and 20 failures, 10 flags, 100 of each and 9 failures and asserts each is reported; it was red against the substring and is green against the anchored pattern. The pattern allows a carriage return before the end of the line, because the `qe` fix-review round 2 (ticket `9015d3d4531c480b`) measured a clean summary ending in CRLF reported as drift by the anchored pattern where the substring had been silent; the test asserts that one silent too, and round 3 (ticket `0c58089cca344063`) measured the guard speaking on `10 failure(s), 0 flag(s)` and `0 failure(s), 10 flag(s)` ending in CRLF, on a doubled CR and on a trailing space. A failure also exits `freshness` non-zero, which the guard discards with `|| true`; the count is what it reads, so the count is what is held.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- README.md · standing · cites-as-live
