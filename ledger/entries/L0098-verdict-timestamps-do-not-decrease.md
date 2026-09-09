---
id: L0098-verdict-timestamps-do-not-decrease
kind: claim
stated: 2026-09-08T02:30:58-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: f80771705f1635a4c0ca16d852f5a7ef87bc13e308827f250f9d3a4f548c02b2
---

## Assertion

Verdict timestamps do not decrease down the file, and none precedes the entry's own stated time.

## Scope

metric: whether an out-of-order verdict timestamp is reported
cohort: entries carrying verdicts
condition: the file's order is what every other verdict rule reads

## Grounds

- code: src/claims_ledger/validate.py § "check_verdicts" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_verdicts carries the latest timestamp it has seen, starting from the entry's stated time, and reports a break once for the whole entry rather than per verdict. Every other rule about verdicts treats the file's order as the order things happened in — what may follow a terminal verdict, which superseded verdict is the one that counts — so a file whose order disagrees with its timestamps is one where those rules are being applied to a sequence that never occurred.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
