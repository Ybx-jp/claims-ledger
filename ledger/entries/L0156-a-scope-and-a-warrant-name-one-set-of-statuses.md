---
id: L0156-a-scope-and-a-warrant-name-one-set-of-statuses
kind: claim
stated: 2026-09-08T10:05:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 726de648b551f881fe1a6046fdf99059f6e7d2419c8d9b65520b7ae58eb5b911
---

## Assertion

An entry whose Scope names the fallen statuses and only those, while its Assertion or Warrant argues from terminality, is flagged rather than refused.

## Scope

metric: whether an entry scoped to one of the two nested status sets and reasoning from the other is reported
cohort: entries whose Scope names refuted, superseded and retracted and never the word terminal
condition: the entry's own status is not terminal, and the test is on words rather than on sense

## Grounds

- code: src/claims_ledger/validate.py § "wider_than_its_scope" @f8b21e96f8e17ea36b344e076672f701398b3b95
- code: src/claims_ledger/validate.py § "check_sections" @f8b21e96f8e17ea36b344e076672f701398b3b95

## Warrant

wider_than_its_scope reads the Scope for status words and returns what the Assertion and Warrant name when the Scope named the three falls and nothing wider; check_sections turns that into a flag, so the run still exits zero. The two sets are nested and differ by non-comparable alone, which is why prose can move between them without any other checker objecting: every rule this schema states about a fallen entry is a rule about what may follow its last verdict, and that is a property of terminality. A failure would be wrong here because both repairs are legal and only the author knows which claim was made; a terminal entry is exempt because its Scope is frozen and a report against it would name a repair nobody can make.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T12:02:06-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_sections" @f8b21e96f8e17ea36b344e076672f701398b3b95
  artifact: 0ddb75eb47ef7188f6f4c1be6d9f6f78ea5387dd
  note: propagated from a moved ground

- 2026-09-08T12:05:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_sections" @aadceb0aba82a85fe71b15394896c43977751709
  note: read against the change in commit aadceb0, which partitioned the grounds into the supporting and the distinguishing ones earlier in the same section; the flag block this claim names is unchanged

## References

- src/claims_ledger/validate.py · standing · cites-as-live
- src/claims_ledger/neighbours.py · standing · cites-as-live
