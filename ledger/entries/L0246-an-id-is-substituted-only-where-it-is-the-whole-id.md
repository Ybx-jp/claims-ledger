---
id: L0246-an-id-is-substituted-only-where-it-is-the-whole-id
kind: claim
stated: 2026-09-14T20:20:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 0ca0f500a8930425f05959e3eb532452fedac14991d12fe0f970817f56658603
---

## Assertion

A renumber substitutes an id only where the text is that whole id, and never where it is the front of a longer one.

## Scope

metric: which occurrences of a moved id a rewrite replaces
cohort: every id that is a textual prefix of another id the ledger holds
condition: two ids share a number and one slug begins with the other

## Grounds

- code: src/claims_ledger/renumber.py § "substitutions" =sha256:ddc3911328bdba06f06757f9da961532883243b380d953fcb183d6352299b001

## Warrant

Both patterns end in a negative lookahead refusing a word character and a hyphen, rather than in a word boundary: a slug ends in a word character and a hyphen is not one, so a boundary alone matches the front of a longer id. Measured before the change: substituting A0002-beta for A0003-beta over `id: A0002-beta-claim` produced `id: A0003-beta-claim`.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-14T21:05:00-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/renumber.py § "substitutions" =sha256:ddc3911328bdba06f06757f9da961532883243b380d953fcb183d6352299b001
  artifact: sha256:6d042a2d299faf997279cd899b9db94e502a9445cd477a6a774362dd6d1a2d1d
  note: propagated from a moved ground

- 2026-09-14T21:05:02-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/renumber.py § "substitutions" =sha256:377ea26f88e1e1b4f955807b740ed0cbef6ea1a7c06a36732a0c4b5261a6ae55
  note: re-read after the commit that answers the gate's second round. The lookahead this claim rests on is unchanged on both patterns; what moved is that the bare-number pattern is now sometimes not emitted at all, which cannot make a prefix match where the lookahead refuses one.

## References

- src/claims_ledger/renumber.py · standing · cites-as-live
