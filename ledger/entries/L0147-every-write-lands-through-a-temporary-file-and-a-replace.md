---
id: L0147-every-write-lands-through-a-temporary-file-and-a-replace
kind: claim
stated: 2026-09-08T02:46:26-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 4718e2eb3440fd7125549eda7f7b7cf4a43e6ad4b830a9910e75042fbd7e06d6
---

## Assertion

Every write in this package lands through a temporary file in the same directory and an atomic replace, so a reader sees either the old file entire or the new one entire.

## Scope

metric: whether a write that fails partway can leave a truncated file
cohort: entries, the registry, cached source bytes, the configuration and the hook
condition: a write may fail on a full disk, a quota or a resource limit

## Grounds

- code: src/claims_ledger/schema.py § "write_bytes_atomically" @4af0acd253eeef1571cd7615ea3a041eda9e945e
- code: src/claims_ledger/schema.py § "write_text_atomically" @4af0acd253eeef1571cd7615ea3a041eda9e945e

## Warrant

write_bytes_atomically writes and flushes a temporary file, syncs it, then replaces the target, and removes the temporary file on any failure. Truncating the destination before knowing the write could be completed is what left a committed entry cut off mid-verdict with the rest gone — the file the ledger is supposed to be the record in. The replacement keeps the permissions the file had, and the directory is synced afterwards, so what survives a crash is a whole file under the right name.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
