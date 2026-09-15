---
id: L0242-two-entries-may-not-carry-one-number
kind: claim
stated: 2026-09-14T19:19:01-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: f179b8c4bfa977dcfa60a962b250f098930fe506ceaebd9b53f0b585bb34eadf
---

## Assertion

Two entries carrying one number are a failure, reported once for the number and naming every entry that carries it.

## Scope

metric: what validate reports over a ledger holding a duplicated number
cohort: every entry in the ledger, taken together
condition: the entries are compared by number, with the slug set aside

## Grounds

- code: src/claims_ledger/validate.py § "check_numbers" =sha256:84d50e9438dca8fb72303e43c671ccafeb9ee4876612807a9d12d67c75d581d3

## Warrant

check_numbers groups every entry by the number its id carries and reports a failure for each number more than one entry answers to, listing them all in the one report; run calls it over the whole entry set, so the question is asked of the ledger rather than of an entry.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-14T21:14:18-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_numbers" =sha256:84d50e9438dca8fb72303e43c671ccafeb9ee4876612807a9d12d67c75d581d3
  artifact: sha256:ffca3242d3dd75caff51d924db3880def8f3ad3520e76d86f39026b197da9f0a
  note: propagated from a moved ground

- 2026-09-14T21:14:19-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_numbers" =sha256:ffca3242d3dd75caff51d924db3880def8f3ad3520e76d86f39026b197da9f0a
  note: re-read after the commit that answers the gate's remaining findings. The section skips an id that does not parse as a number, which is the one input on which its report could not be true. Every entry with a well-formed id is grouped and reported exactly as before, which is what this claim is about.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
- docs/OPERATING.md · standing · cites-as-live
