---
id: L0311-the-pin-guard-reads-the-whole-report
kind: claim
stated: 2026-10-01T00:54:12-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: d8c83b237e261158cba1d6363748496ef1e9ec3cafd9fa1841e59b159ee7fa8d
---

## Assertion

The pin guard reads a clean freshness report as clean however much of the report follows its summary line.

## Scope

metric: whether the pin guard reports drift on a freshness report
cohort: a report whose summary line is followed by more than a pipe buffer and less than one argument's limit of further lines
condition: the guard runs under `set -o pipefail`, as every shipped hook does

## Grounds

- code: tests/test_harness.py § "test_the_pin_guard_reads_the_whole_report_however_much_follows_the_summary" =sha256:62bcedaae64adeb910d274f6d5014ad1b4a485f9aa625c6f0cd6e43b84dae13e

## Warrant

The pin guard asks whether the report contains `0 failure(s), 0 flag(s)`. Through `printf | grep -q` under `pipefail`, `grep` exits at the match, a writer still holding more than a pipe buffer dies of SIGPIPE, the negated test turns true, and a clean report is reported as a drifted pin. The test hands the guard a stand-in interpreter whose report is a clean summary with 100 KB behind it and asserts silence, then the same bulk behind a report that is not clean and asserts the drift is spoken, so a guard that never speaks cannot pass. It was red against the pipe in 20 runs of 20 and is green against the here-string. `freshness` prints its summary last, so no report it writes today reaches this. The bulk stays below 128 KB because above that the guard's `jq --arg` fails and it says nothing either way, which is #77 and not this claim.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- CLAUDE.md · standing · cites-as-live
