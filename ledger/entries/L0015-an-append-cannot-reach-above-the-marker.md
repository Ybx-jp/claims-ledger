---
id: L0015-an-append-cannot-reach-above-the-marker
kind: claim
stated: 2026-09-07T22:47:42-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 143f9aec9f0c20a60e919dbc791fc4aacc875be6e49f16847748241120fdd8ad
---

## Assertion

Appending a verdict never changes the region above the APPEND marker: the insertion point is searched only below the marker, and an assembled text that would alter the region above it is refused rather than written.

## Scope

metric: the bytes above the APPEND marker, before and after an append
cohort: every verdict appended into an entry file by the propagation machinery
condition: any entry layout, including one whose References heading sits above the marker

## Grounds

- code: src/claims_ledger/propagate.py § "append_verdict" @e80ad36e50c2c2a2afab6603592ff5fb1818f89e

## Warrant

append_verdict partitions the entry text at the APPEND marker and searches for the References heading in the appendable half alone, so a heading above the marker cannot be chosen as an insertion point. It then re-partitions the assembled text and raises rather than writes unless the head is byte-identical to the head it started with, so no path reaches the write with the region above the marker changed.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-07T23:20:05-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/propagate.py § "append_verdict" @e80ad36e50c2c2a2afab6603592ff5fb1818f89e
  artifact: 5599aaa78e6bd3f74622dee9b5baab4e44c37199
  note: propagated from a moved ground

- 2026-09-07T23:22:00-07:00 · superseded · grade: measured · author: main
  evidence: entry: L0028-an-append-cannot-reach-above-the-marker · supersedes
  note: a docstring gained three citations inside the pinned section; the Assertion, Scope, Warrant and Backing are carried across unchanged and the successor re-pins the same section

## References
