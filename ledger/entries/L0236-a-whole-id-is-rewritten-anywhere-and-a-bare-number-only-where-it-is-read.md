---
id: L0236-a-whole-id-is-rewritten-anywhere-and-a-bare-number-only-where-it-is-read
kind: claim
stated: 2026-09-14T19:13:42-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 5970efc85350e121f21aa1146f2f2c33e09753159ceaedfd2443c9a7e7205830
---

## Assertion

A renumber rewrites a whole id wherever it appears, and a bare number only in the entries and in the documents a citation is read from.

## Scope

metric: which occurrences of a moved id a rewrite replaces
cohort: every text file in each rewritten commit
condition: the substitution is of a whole id or of its number alone

## Grounds

- code: src/claims_ledger/renumber.py § "substitutions" =sha256:781071fd7abad954e1dae656e34c35e50161ff901e2da9e8d134e8449ffe4afc

## Warrant

substitutions builds one pattern for the whole id, applied to every file, and one for the bare number carrying a flag that substitute honours only where the caller says an id is what a number means; a whole id is distinctive enough to be safe anywhere, and a bare number is not.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-14T20:21:10-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/renumber.py § "substitutions" =sha256:781071fd7abad954e1dae656e34c35e50161ff901e2da9e8d134e8449ffe4afc
  artifact: sha256:ddc3911328bdba06f06757f9da961532883243b380d953fcb183d6352299b001
  note: propagated from a moved ground

- 2026-09-14T20:21:11-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/renumber.py § "substitutions" =sha256:ddc3911328bdba06f06757f9da961532883243b380d953fcb183d6352299b001
  note: re-read after the commit that fixes what the pre-merge gate found. The right-hand boundary of both patterns changed from a word boundary to a lookahead refusing a word character or a hyphen, which is a correction to where an id is recognised and not to which files each pattern reaches: the whole id still goes everywhere and the bare number still only where a number is read as an id.

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
