---
id: L0154-a-terminal-entrys-grounds-are-immutable-history
kind: claim
stated: 2026-09-08T09:39:51-07:00
author: main
grade: measured
supersedes: L0043-a-fallen-entrys-grounds-are-immutable-history
verbatim_change: the Scope metric and cohort now name the terminal statuses rather than the fallen ones, which is the set the checker tests; Backing is unchanged and there is none
verbatim_sha: aa09795a52b7b125e4e15f14488898e43ea30627ddc33cce9bae64c0958cae2c
---

## Assertion

The grounds of an entry whose own status is terminal are exempt from the act check, so a refuted, superseded, retracted or non-comparable entry is not reported for citing a target that fell after it.

## Scope

metric: whether the grounds of a terminal entry are held to their targets' current statuses
cohort: entries whose derived status is terminal
condition: such an entry holds a ground citing a target that has since fallen

## Grounds

- code: src/claims_ledger/references.py § "run" @5ee55ae6992f10c834510759f026644f42614025
- code: src/claims_ledger/schema.py § "TERMINAL" @5ee55ae6992f10c834510759f026644f42614025

## Warrant

run tests an entry's status against TERMINAL and skips it before reading its grounds at all. What makes such a report unanswerable is terminality rather than a fall: the Grounds sit in the frozen region and cannot be edited, and no verdict may follow a terminal status, so an entry that is non-comparable has exactly the same nothing to offer as a refuted one. The predecessor tested FALLEN, which left non-comparable entries reported for an act no repair could reach.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T12:02:06-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/references.py § "run" @5ee55ae6992f10c834510759f026644f42614025
  artifact: 703e655370f9a36ce54602a2d3ef776f6d165a33
  note: propagated from a moved ground

- 2026-09-08T12:05:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/references.py § "run" @aadceb0aba82a85fe71b15394896c43977751709
  note: read against the change in commit aadceb0, which added the report for a citation-shaped parenthesis whose act is not a citation act; that loop reads documents and the terminal exemption this claim names is untouched

## References

- src/claims_ledger/references.py · standing · cites-as-live
