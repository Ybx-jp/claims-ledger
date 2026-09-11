---
id: L0198-a-discharge-records-the-digest-this-run-sees
kind: claim
stated: 2026-09-10T22:03:58-07:00
author: main
grade: measured
supersedes: L0103-a-discharge-records-what-this-run-sees-or-what-the-path-held
verbatim_sha: 005bd576f9072bfabe5fcc2778d7af904d5ab5651d0cf0691ad9b53db4669d70
---

## Assertion

A propagated verdict discharges the drift in front of it only when it records the digest this run reads the section as, or absent for a ground that is gone; a record of an earlier drift the artifact has since moved on from, or an object id recorded before anchors could be stated by value, discharges nothing.

## Scope

metric: what a verdict has to record before it silences a live finding
cohort: contested verdicts by the propagation author naming a drifted ground
condition: the drift may be uncommitted, or committed and since changed again

## Grounds

- code: src/claims_ledger/freshness.py § "discharges" =sha256:cd3840006b135d1fe234918eb203713be41e03f1c390c3ffc20a6087fb40199c

## Warrant

discharges compares the verdict's recorded artifact against the digest drift computed from the same read the comparison used, and returns true only on equality; it asks nothing of history. Matching by pointer alone was the whole of the old rule, and it made the recorded artifact unreachable in the state a discharge normally lives in. An earlier rule then accepted a record that history could confirm the path had held, which silenced a ground for the life of its entry once any drift had been recorded; holding the record to the artifact in front of the run instead means a further change after a recorded drift is reported as news, and a whole file's object id, which names no section, can never equal a section digest.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/freshness.py · standing · cites-as-live
