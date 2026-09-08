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

## References

- src/claims_ledger/schema.py · standing · cites-as-live
