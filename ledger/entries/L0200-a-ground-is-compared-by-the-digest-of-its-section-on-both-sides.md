---
id: L0200-a-ground-is-compared-by-the-digest-of-its-section-on-both-sides
kind: claim
stated: 2026-09-10T22:03:59-07:00
author: main
grade: measured
supersedes: L0009-a-section-pin-compares-its-section-or-says-it-could-not
verbatim_change: the Scope condition names the anchor rather than the pin, since a ground may now be anchored by value; Backing is unchanged and there is none
verbatim_sha: a794f658fa1274644509f44c8ec489424e55c5a94733c8971450af40097d5975
---

## Assertion

A ground is compared by the digest of its named section, read through one decode on both sides, so an edit elsewhere in the file is not its drift, and a side that could not be read at all is reported as a comparison that did not happen rather than as drift.

## Scope

metric: the freshness finding for a sectioned ground
cohort: grounds of a sectioned evidence type
condition: the section differs from the anchor, or cannot be read

## Grounds

- code: src/claims_ledger/freshness.py § "drift" =sha256:ec78ecef0788830e1fe16fe77e34d9d23292efbc3622b7af29e1defa9a216ff6

## Warrant

drift takes the anchor's digest from anchor_digest and the tree's from the same section_text and digest_of applied to the artifact as this run reads it, decoded as UTF-8 through universal newlines on both sides, and reports moved only when the two differ. Nothing narrower than the section is compared, so an edit outside it leaves the digest alone; a side whose bytes cannot be reached at all is unknown with the reason, so no comparison it did not make is recorded as one it did. The comparison is no longer version control's own diff, which applied the repository's filters to both sides but could not be narrowed to a section and needed the anchor to be a commit.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- docs/FRESHNESS.md · standing · cites-as-live
- src/claims_ledger/freshness.py · standing · cites-as-live
