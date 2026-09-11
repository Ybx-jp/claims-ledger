---
id: L0090-an-assertion-carries-no-quotation-marks
kind: claim
stated: 2026-09-08T02:30:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 879efc264a7357e5b313344eb121a089846ae18ddd2811e56e0253af999c4c42
---

## Assertion

An Assertion containing a quotation mark fails: source words live in Backing, where they are checked against the source that supplied them.

## Scope

metric: whether a quotation mark in an Assertion is reported
cohort: the Assertion of every entry
condition: straight and typographic marks alike

## Grounds

- code: src/claims_ledger/validate.py § "check_sections" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_sections tests the Assertion against both straight and typographic quotation marks and fails on any of them. A quotation in the Assertion wears the authority of a source while resolving to nothing: the resolver checks Backing spans against the bytes of the source that supplied them, and an Assertion is never read that way. Moving the words down to Backing is what makes them checkable at all.

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
- 2026-09-11T03:10:33-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_sections" @f8b21e96f8e17ea36b344e076672f701398b3b95
  artifact: sha256:c0769a66c50f5c4553287e21260b05a456a756669f8783622ff6a5f7b6179afc
  note: propagated from a moved ground
- 2026-09-11T03:10:33-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_sections" =sha256:c0769a66c50f5c4553287e21260b05a456a756669f8783622ff6a5f7b6179afc
  note: read against the working tree after check_sections gained the every-ground-is-a-distinction rule and the ENTRY_ACTS check since the reading at f8b21e9: the test of the Assertion against straight and typographic quotation marks is untouched; the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
