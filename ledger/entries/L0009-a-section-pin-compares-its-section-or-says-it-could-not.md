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

## References

- docs/FRESHNESS.md · standing · cites-as-live
- src/claims_ledger/freshness.py · standing · cites-as-live
