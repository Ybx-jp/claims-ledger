---
id: L0103-a-discharge-records-what-this-run-sees-or-what-the-path-held
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 005bd576f9072bfabe5fcc2778d7af904d5ab5651d0cf0691ad9b53db4669d70
---

## Assertion

A propagated verdict suppresses a finding only when it records the artifact this run is looking at, or an artifact the path really held between the pin and here.

## Scope

metric: what a verdict has to record before it silences a live finding
cohort: contested verdicts by the propagation author naming a drifted ground
condition: the drift may be uncommitted, or committed and since changed again

## Grounds

- code: src/claims_ledger/freshness.py § "discharges" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848
- code: src/claims_ledger/freshness.py § "caused" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

discharges compares the verdict's recorded artifact against what this run reads, and otherwise asks caused whether the path ever held that artifact between the pin and now. The two cover different moments: the first is the ordinary pre-commit case, where the drift is in the working tree or the index and is in no commit for a history walk to find; the second is the case after the drift is committed, and it survives the artifact changing again afterwards. Matching by pointer alone was the whole of the old rule, and it made the recorded artifact unreachable in the state a discharge normally lives in.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
