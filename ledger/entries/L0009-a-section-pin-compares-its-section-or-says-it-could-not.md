---
id: L0009-a-section-pin-compares-its-section-or-says-it-could-not
kind: claim
stated: 2026-09-07T19:10:36-07:00
author: main
grade: measured
supersedes: L0008-a-section-pin-compares-only-its-section
verbatim_change: the Assertion and the Scope condition now name the case where a side cannot be read; Backing is unchanged and there is none
verbatim_sha: 1534d36831830e327217bdb5e65e1cef2fca2f4109aede5e3fc42865429284d2
---

## Assertion

When a pinned ground names a section, freshness compares only that section between the pin and the working tree, so an edit elsewhere in the file is not drift, and a side it could not read at all is reported as a comparison that did not happen rather than as drift.

## Scope

metric: the freshness finding for a sectioned ground
cohort: grounds of a sectioned evidence type
condition: the file differs from the pin, or cannot be read

## Grounds

- code: src/claims_ledger/freshness.py § "scoped" @7b1f34145b2847f8f0037a3b420cbfaed0389b5a

## Warrant

scoped extracts the named section from both texts through the project's section pattern and reports moved only when the two sections differ after trailing whitespace is stripped; when either side cannot be reached at all it reports unknown with the reason, so no comparison it did not make is recorded as one it did.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T19:39:24-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/freshness.py § "scoped" @7b1f34145b2847f8f0037a3b420cbfaed0389b5a
  artifact: e2386c2564c931207a03de464b78a3bae971afac
  note: propagated from a moved ground

- 2026-09-08T19:40:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "scoped" @225f5867b2591ffc5b3020dfe20ca407d81ee06f
  note: read against commit 225f586, which moved `ARCH-AUDIT.md` into `docs/audits/` and rewrote the mentions of it in this section; the section was parsed at the pin and at that commit and compared with comments and docstrings set aside, and the two are identical, so nothing the claim rests on changed
- 2026-09-10T22:05:55-07:00 · superseded · grade: measured · author: main
  evidence: entry: L0200-a-ground-is-compared-by-the-digest-of-its-section-on-both-sides · supersedes
  note: scoped was folded into drift, which compares the section by digest on both sides and no longer needs the anchor to be a commit; the Scope condition names the anchor rather than the pin

## References
