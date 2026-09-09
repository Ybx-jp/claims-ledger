---
id: L0036-quoted-spans-are-found-in-source-order
kind: claim
stated: 2026-09-08T02:02:28-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 04e04117ecc0f001e73dbadadf5b8e66385641f9c3bc6b6d307268ff1ec8b1ab
---

## Assertion

The spans of a Backing quote are each located after the end of the span before them, so a quote that verifies is a forward walk of its source.

## Scope

metric: the position at which each span after its predecessor is searched for
cohort: Backing quotes carrying more than one span
condition: every span occurs somewhere in the source

## Grounds

- code: src/claims_ledger/resolve.py § "check_quote" @ec82c16045421ce5a6cb71befe8ddbe6067489ae

## Warrant

check_quote carries a cursor that is advanced past each located span, and the search for the next span begins there. A span occurring only before the cursor is reported as failing to be a contiguous span of the source after the preceding one, and the block fails. Text assembled from passages presented in an order the source does not have therefore does not verify.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
