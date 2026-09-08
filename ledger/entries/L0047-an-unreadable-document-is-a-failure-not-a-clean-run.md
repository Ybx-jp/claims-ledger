---
id: L0047-an-unreadable-document-is-a-failure-not-a-clean-run
kind: claim
stated: 2026-09-08T02:08:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0de37bc16bdd8be501e2e7b73c455ed98a270f634191361261f00f9ca9e58ccf
---

## Assertion

A configured document the checker could not open or decode is reported as a failure, so a run that read fewer documents than the configuration names cannot exit clean.

## Scope

metric: the outcome for a configured document that could not be read
cohort: documents named by the configuration, whether they fail at discovery or at the read
condition: the rest of the ledger checks clean

## Grounds

- code: src/claims_ledger/references.py § "run" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487

## Warrant

run reports both populations: the documents discovery could not open, which the ledger carries alongside the ones it could, and the ones that fail at the read here. Each is a failure rather than a flag, because the exit code is what a hook acts on, and a document whose citations were never read is a document over which nothing was verified.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/references.py · standing · cites-as-live
