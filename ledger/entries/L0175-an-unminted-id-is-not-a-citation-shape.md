---
id: L0175-an-unminted-id-is-not-a-citation-shape
kind: claim
stated: 2026-09-08T18:15:07-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 98bef01ba56eade7986754c32f3e942f43fecb964a49ed8a7ed4892452cefd32
---

## Assertion

A parenthesis in a document holding an id, a comma and an act-shaped word is reported as a
miscitation when the id names an entry this ledger holds, and is passed over by that rule when
it does not.

## Scope

metric: whether a citation-shaped parenthesis is reported
cohort: every document the configuration reaches
condition: the word is not a citation act; the id's series is not quarantined; the id is matched on series and number

## Grounds

- code: src/claims_ledger/references.py § "run" @6865d617f85111766795cb98b2075d5bde81822d
- entry: L0176-a-citation-shaped-parenthetical-names-a-citation-act · distinguishes

## Warrant

L0176 says the report fires; this says where it stops. The two are read off the same loop and
they are different claims: one is about the word after the comma, this one is about the id
before it. The pattern is a shape, and the shape by itself is ordinary prose — a capital, three
digits or more, a comma and a lowercase word is every lint code there is, so a rule that read
the shape alone failed a commit over a waiver in a source comment, in exactly the projects that
put their source files in the document list. Which ids are a citation of this ledger is a thing
the ledger knows and a regular expression does not, so the loop asks it, matching on series and
number so that a wrong or missing slug is still caught. Passed over here is not passed over
everywhere: an id in a quarantined series is the archive rule's finding, reported under its own
name a few lines earlier, and this rule leaves it to that one rather than naming the same
parenthesis twice. What is given up is a mistyped act on an id that also does not exist. That
is not beyond recovery — a word that is a proper prefix of a citation act separates a mistyped
`cites-as-liv` from an ordinary `unresolved` — but recovering it is a second rule with an
outcome of its own to choose, and this entry does not make it. The coupling this buys is worth
saying: a parenthesis that is prose today becomes a failure the day an entry is minted at its
number, so the population the rule reads grows with the ledger rather than staying fixed.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-11T19:41:48-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/references.py § "run" =sha256:166a79c96b6b68db961e4aeb6e8a271e668650a3181d75583405ee4478808d6f
  note: re-read after the commit that gives this checker a cached mode: it takes the flag, loads the entries with it, and reads each configured document from the index where the index holds it. Every rule this claim is about is unchanged — what moved is which tree the text being checked was read from, and the bodies being read once for the run instead of once per loop.
- 2026-09-20T12:55:58-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/references.py § "run" =sha256:166a79c96b6b68db961e4aeb6e8a271e668650a3181d75583405ee4478808d6f
  artifact: sha256:51cf8c55f336e8fd07780a8e4509a9f7645490b4096cd3531b71f499615e89d7
  note: propagated from a moved ground

- 2026-09-20T12:56:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/references.py § "run" =sha256:51cf8c55f336e8fd07780a8e4509a9f7645490b4096cd3531b71f499615e89d7
  note: re-read after the commit that lets a marker name its entry by the series and number alone. The document loop in this section now resolves each marker through `cited_target` and collects the resolved id rather than the text of the marker, and the slug rule is asked after the lookup. The rule is untouched and the set it asks is the same set, now built from the number index rather than by splitting each id again — the numbers are identical, and it was already the number this rule compared.


## References

- src/claims_ledger/references.py · standing · cites-as-live
