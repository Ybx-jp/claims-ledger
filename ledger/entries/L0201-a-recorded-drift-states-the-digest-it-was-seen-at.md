---
id: L0201-a-recorded-drift-states-the-digest-it-was-seen-at
kind: claim
stated: 2026-09-10T22:03:59-07:00
author: main
grade: measured
supersedes: L0104-the-artifact-is-recorded-as-the-id-a-commit-would-store
verbatim_change: the cohort now includes verdicts for a withdrawn ground, which record their absence the same way; Backing is unchanged and there is none
verbatim_sha: bee4052241850677c163f17950feff08a7728a3e74684085a0d8db3355c9d0a0
---

## Assertion

The artifact a propagated verdict records is the digest of the section as this run read it, computed from the same read the comparison used, the digest of the whole text for a plain anchor or of the bytes where the artifact is not text, and absent where the ground is gone.

## Scope

metric: what value is recorded as the artifact a drift was seen at
cohort: verdicts appended for a moved or withdrawn ground
condition: the drift is ordinarily in the working tree and in no commit yet

## Grounds

- code: src/claims_ledger/freshness.py § "drift" =sha256:ec78ecef0788830e1fe16fe77e34d9d23292efbc3622b7af29e1defa9a216ff6

## Warrant

drift carries the digest of what it read out in the same result as the finding, so what a verdict records is exactly what the comparison compared and not a second reading of the file; run writes that value into the verdict block. A commit id would not do, because the ordinary case is a drift that is not yet committed at all, which is what a pre-commit hook exists for; an object id of the whole file, which the earlier rule recorded, names no section and cannot be compared with one. A ground that is gone has no text to digest, and its absence is the thing that happened.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-12T15:32:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/freshness.py § "drift" =sha256:33c2c162d1481a0cca280d3b703aee8ae0342c09f1c287831340905d0213540e
  note: acknowledged: `drift` threads the ledger down so its two cached reads can name the path the index holds. Nothing about what counts as drift changed (L0232).

## References

- src/claims_ledger/freshness.py · standing · cites-as-live
