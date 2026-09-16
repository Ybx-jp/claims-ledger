---
id: L0273-a-lifted-passage-is-appended-and-never-frozen
kind: claim
stated: 2026-09-15T17:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 59183bd13326f9b0b23b64f458997c91a4697f6841ad1e65c3170b8c8bdb67ce
---

## Assertion

Prose lifted out of an artifact is appended below the APPEND marker rather than written into the frozen region, so a lift onto an entry that is already committed costs no supersession.

## Scope

metric: where a lifted passage is written in an entry file
cohort: the Passages section and the frozen-region comparison
condition: an entry that already exists in a commit

## Grounds

- code: src/claims_ledger/schema.py § "TAIL_SECTIONS" =sha256:00950543b82056640568b05b4b3e84febd2d7e425c016ab618fffd56871e14a6
- code: src/claims_ledger/lift.py § "append_passage" =sha256:02107d43a7bdc75836afd55b7b840d3246e7aa9c11806e1408eb5a74323af37b

## Warrant

The frozen region is compared against the blob at the creating commit, including the bytes no section owns, so a section added above the marker on a committed entry fails that comparison however well formed it is. Appending below the marker leaves every frozen byte alone, which is what lets an existing entry take a passage at all.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/lift.py · standing · cites-as-live
- src/claims_ledger/schema.py · standing · cites-as-live
