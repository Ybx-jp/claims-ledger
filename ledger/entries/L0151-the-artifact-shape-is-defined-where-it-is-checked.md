---
id: L0151-the-artifact-shape-is-defined-where-it-is-checked
kind: claim
stated: 2026-09-08T02:46:27-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: f8d9d7f104287f799687c1330f0e6676db205ff5085a4950d88c454093efef2f
---

## Assertion

The shape a propagated verdict's recorded artifact must take is defined beside the checker that holds it to that shape, rather than beside the code that writes the value.

## Scope

metric: where the constants defining the artifact record live
cohort: the absent marker, the object-id pattern and the null object id
condition: one checker writes the value and another validates it

## Grounds

- code: src/claims_ledger/schema.py § "OBJECT_ID_RE" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "ABSENT" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "NULL_OBJECT_ID" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

The three constants sit in the schema both checkers import. A rule enforced only by the code that writes a value is a rule a hand-edited entry walks straight past, and the entries are files a person edits: the validator is the checker that reads every verdict in every state, so the shape has to be stated where it can. Keeping them here also means the writer and the validator cannot come to disagree about what an absent artifact is spelled as.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/schema.py § "ABSENT" @4af0acd253eeef1571cd7615ea3a041eda9e945e
  artifact: 36052faf227379aac7e17f339c1c6b3937d1f6c1
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "ABSENT" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed

- 2026-09-11T19:30:01-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "OBJECT_ID_RE" =sha256:839f612a1927030849314c6a1fc1edeac16800b4e55ae033fb73889b32521948
  note: re-read after the commit that widens an object id to the repository's own hash width. The shape is still defined here, beside the checker that holds a verdict to it and not beside the code that writes the value, which is the whole of this claim; only the width it admits moved.

## References

- src/claims_ledger/schema.py · standing · cites-as-live
