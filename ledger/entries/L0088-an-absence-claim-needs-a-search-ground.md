---
id: L0088-an-absence-claim-needs-a-search-ground
kind: claim
stated: 2026-09-08T02:30:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: c87606ba46d1fc05e679433a66f18ea4a0834d15a8a127170c4e601123bb57d9
---

## Assertion

An Assertion that reads as an absence or a priority claim fails unless the entry carries a search ground.

## Scope

metric: whether an absence or priority Assertion lacking a search ground is reported
cohort: the Assertion of every entry
condition: the test is on words rather than on sense

## Grounds

- code: src/claims_ledger/validate.py § "check_sections" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/validate.py § "is_absence_claim" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/validate.py § "ABSENCE_WORDS" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

is_absence_claim applies the heuristic the corpus README states — a short list of trigger words, two fixed phrases, and the word `no` followed within its own sentence by one of six others — and check_sections requires a search ground whenever it fires. A claim that something is absent, or that this project got somewhere before anyone else, rests on having looked rather than on having built; the search ground is the record of the looking, and the heuristic errs toward asking for it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T10:05:05-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_sections" @34f416118e10a14169475fe23d3176d347d0ed8d
  artifact: dcebe963e990823a9449a085659c86c005628252
  note: propagated from a moved ground

- 2026-09-08T10:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_sections" @f8b21e96f8e17ea36b344e076672f701398b3b95
  note: read against the change in commit f8b21e96, which added a flag block at the end of check_sections and a wording heuristic beside FALSIFIER_RE; this rule is stated elsewhere in the same section and is unaffected

## References

- src/claims_ledger/validate.py · standing · cites-as-live
