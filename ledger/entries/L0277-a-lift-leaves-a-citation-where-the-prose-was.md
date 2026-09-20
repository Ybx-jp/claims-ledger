---
id: L0277-a-lift-leaves-a-citation-where-the-prose-was
kind: claim
stated: 2026-09-20T10:22:13-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6fa8403856857b5e58566bcce3f65793a0d62415769858bc0da51305aef6091b
---

## Assertion

A lift writes a citation of the lifting entry where it takes the prose from, unless the section already carries one.

## Scope

metric: what the artifact holds at the site the prose came out of
cohort: a lift out of a section carrying no citation of the lifting entry
condition: the prose is docstring body, which is all a lift takes

## Grounds

- code: src/claims_ledger/lift.py § "marker_for" =sha256:18c75889ee0cef7d08663a5bc287557b9f0301de357655861b04270f42d0c989

## Warrant

A lift is a deletion, and a deletion that leaves no id leaves nothing to trace: the prose is on the entry, and the file says neither which entry nor that there was prose. The only signal is a freshness flag saying the section moved, which any edit produces and which names no id. marker_for writes the citation where the first run of prose began, and writes none where the section already carries one of this entry, so the file names the entry that holds the prose in every case and the author's own citation is never moved to do it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-20T12:55:58-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/lift.py § "marker_for" =sha256:18c75889ee0cef7d08663a5bc287557b9f0301de357655861b04270f42d0c989
  artifact: sha256:cbae04449dfb73e10b0dfd920e15f6ba42d45490dfebccdbeb144e8d30231a70
  note: propagated from a moved ground

- 2026-09-20T12:56:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/lift.py § "marker_for" =sha256:cbae04449dfb73e10b0dfd920e15f6ba42d45490dfebccdbeb144e8d30231a70
  note: re-read after the commit that lets a marker name its entry by the series and number alone. The section now recognises an existing marker in either spelling and chooses the spelling it writes from the project's rule and from whether the artifact is a document. What this claim asserts is untouched: a lift still leaves a citation where the prose was, and it is still an ordinary citation held to the entry's status rather than a form of its own.


## References

- src/claims_ledger/lift.py · standing · cites-as-live
- README.md · standing · cites-as-live
