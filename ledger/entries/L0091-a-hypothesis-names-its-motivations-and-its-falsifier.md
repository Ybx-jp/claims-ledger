---
id: L0091-a-hypothesis-names-its-motivations-and-its-falsifier
kind: claim
stated: 2026-09-08T02:30:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: b74d9c2743aaf27c48ba6ad0840c43ae9174dce44302f12cecb5253a40196572
---

## Assertion

A hypothesis fails unless it names the entries motivating it and its Warrant says what would falsify it.

## Scope

metric: whether a hypothesis lacking motivating entries or a falsifier is reported
cohort: entries of kind hypothesis
condition: the falsifier test is a heuristic on the Warrant's wording

## Grounds

- code: src/claims_ledger/validate.py § "check_sections" @34f416118e10a14169475fe23d3176d347d0ed8d
- code: src/claims_ledger/validate.py § "FALSIFIER_RE" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_sections requires an entry ground on a hypothesis and searches its Warrant with FALSIFIER_RE, which matches any word beginning falsif. A hypothesis is a bet on a design: without the claims motivating it the roster displays a question nothing connects to, and without a falsifier there is nothing that would ever settle it. The rule is stated as a word test so that a checker author implements what the corpus seeds exercise.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T10:05:05-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_sections" @34f416118e10a14169475fe23d3176d347d0ed8d
  artifact: dcebe963e990823a9449a085659c86c005628252
  note: propagated from a moved ground

- 2026-09-08T10:05:05-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "FALSIFIER_RE" @34f416118e10a14169475fe23d3176d347d0ed8d
  artifact: dcebe963e990823a9449a085659c86c005628252
  note: propagated from a moved ground

- 2026-09-08T10:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_sections" @f8b21e96f8e17ea36b344e076672f701398b3b95
  note: read against the change in commit f8b21e96, which added a flag block at the end of check_sections and a wording heuristic beside FALSIFIER_RE; this rule is stated elsewhere in the same section and is unaffected, and the FALSIFIER_RE ground moved only because a comment was written after it
- 2026-09-10T22:05:57-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_sections" @f8b21e96f8e17ea36b344e076672f701398b3b95
  artifact: sha256:c0769a66c50f5c4553287e21260b05a456a756669f8783622ff6a5f7b6179afc
  note: propagated from a moved ground

- 2026-09-10T22:05:57-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "FALSIFIER_RE" @34f416118e10a14169475fe23d3176d347d0ed8d
  artifact: sha256:57cb73fb5f2618bd69cfeed48ece4d5cf1ae0ab491604e990fa1a3ebc091cc09
  note: propagated from a moved ground
- 2026-09-10T22:06:18-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "FALSIFIER_RE" =sha256:57cb73fb5f2618bd69cfeed48ece4d5cf1ae0ab491604e990fa1a3ebc091cc09
  note: read against the working tree: the regex is unchanged since the pin; the section moved because a comment on the fallen and terminal status sets was written below the assignment in commit f8b21e9, and the earlier reading corroborated check_sections only, so this ground's drift was discharged by a whole-file record that the digest rule no longer accepts; the assertion holds as written.
- 2026-09-10T22:07:28-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_sections" =sha256:c0769a66c50f5c4553287e21260b05a456a756669f8783622ff6a5f7b6179afc
  note: read against the working tree: since the reading at f8b21e9 the section gained the distinguishes-act rules and lost the immutability paragraph from its docstring; the hypothesis rule, an entry ground and a Warrant that names a falsifier, is unchanged, and the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
