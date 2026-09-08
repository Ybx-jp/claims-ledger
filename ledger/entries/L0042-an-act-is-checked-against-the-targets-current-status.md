---
id: L0042-an-act-is-checked-against-the-targets-current-status
kind: claim
stated: 2026-09-08T02:08:33-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: b194b4b79e0f9f9e10425bdfed15a48e1295811d2773221fe2d2b9bfa0f978ea
---

## Assertion

A citation's act is checked against the current status of the entry it names, in both directions — a ground that cites an entry, and a document that cites one — and an act the status does not permit fails.

## Scope

metric: whether an act incompatible with its target's status is reported, from a ground and from a document alike
cohort: entry grounds carrying an act, and inline citations in configured documents
condition: the target entry exists

## Grounds

- code: src/claims_ledger/references.py § "run" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487
- code: src/claims_ledger/schema.py § "ACT_ALLOWS" @c4bcb3db71dbd2bd1c588791a741ecf2fd360487

## Warrant

ACT_ALLOWS is the one table saying which statuses each act may stand against, and run consults it twice over the same derived statuses: once walking the grounds of each entry, once walking the citations found in each document. The two directions therefore cannot drift into two rules. The filter a reader would otherwise apply by hand at every citation is applied here instead, and the report names the act, the target, the status it found and the statuses the act needs.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/references.py · standing · cites-as-live
