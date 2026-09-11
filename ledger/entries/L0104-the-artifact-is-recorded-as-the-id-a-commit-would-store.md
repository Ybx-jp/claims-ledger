---
id: L0104-the-artifact-is-recorded-as-the-id-a-commit-would-store
kind: claim
stated: 2026-09-08T02:37:34-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 5da0e51ecf3eca4712e9bcf5e2a43fa0c330faf3332553bfc50349de71b454cd
---

## Assertion

The artifact a verdict records is the object id version control would store it under, computed so that whatever the repository does to a file on its way in is done here too.

## Scope

metric: what value is recorded as the artifact a drift was seen at
cohort: verdicts appended for a moved ground
condition: the drift is ordinarily in the working tree and in no commit yet

## Grounds

- code: src/claims_ledger/freshness.py § "seen_at" @c1f9f2b89bb28557c7d0b6be9f5d29909677a848

## Warrant

seen_at asks hash-object with the path given, rather than hashing the bytes itself, so line endings and clean filters are applied exactly as a commit would apply them and the recorded id is the one a commit of those bytes would carry. A commit id would not do: the ordinary case is a drift that is not yet committed at all, which is what a pre-commit hook exists for. Under --cached the staged blob's id is asked of the index instead, matching what the rest of the run is reading.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-10T22:05:55-07:00 · superseded · grade: measured · author: main
  evidence: entry: L0201-a-recorded-drift-states-the-digest-it-was-seen-at · supersedes
  note: seen_at was removed: the record is the digest of the section as the comparison read it, not the object id of the whole file; the cohort now includes withdrawn grounds

## References
