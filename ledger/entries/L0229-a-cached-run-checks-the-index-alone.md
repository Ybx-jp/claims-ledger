---
id: L0229-a-cached-run-checks-the-index-alone
kind: claim
stated: 2026-09-12T13:56:18-07:00
author: main
grade: measured
supersedes: L0219-the-entries-under-cached-are-the-ones-the-index-holds
verbatim_change: the Assertion and the Scope condition now say the list is the index's alone rather than the union of the index and the working tree, and the Grounds gain the distinction from L0228 over the document list; Backing is unchanged and there is none
verbatim_sha: ef3fd7b873b3adb2399bbcfd4ad03dfd898f14f70e518c9819cd3637c4370174
---

## Assertion

A run asked for the index draws its list of entries from the index alone, so an entry the commit will not carry is not on the list and cannot answer for a citation of it.

## Scope

metric: which trees the list of entries under `--cached` is drawn from
cohort: every checker run given the cached flag
condition: an index that cannot be asked falls back to the working tree's listing, which the guard already reports

## Grounds

- code: src/claims_ledger/schema.py § "index_entry_files" =sha256:bdba81db096d6c0714bce4866d597ef2cf436fec41ecc7743b2ed4edb0447eed
- code: src/claims_ledger/schema.py § "load_entries" =sha256:9be884cc43f0450776c51595f52fdcab3a3c70ca830aa3d03bce03d702c77f7e
- entry: L0228-documents-under-cached-are-the-ones-the-index-holds · distinguishes

## Warrant

L0219 got half of this right and defended the other half on a reason that does not hold. Listing the working tree under the flag was a false pass and is fixed; taking the union of the two trees was justified there on the ground that checking an entry the commit will not carry "can only cost a report nobody needed". It cannot. The union does not add a spare report, it supplies a citation's target: an entry taken out of the index with `git rm --cached` and left on disk is still on the list, so a document citing it resolves against an entry the commit is dropping. Measured in a throwaway repository with `docs/citer.md` citing entry X `cites-as-live` and X removed from the index that way, all five checkers report `2 entries` and `0 failure(s)` at exit 0, and a fresh clone of the commit that made holds one entry and fails `references` at exit 1 naming the citation. The index is the side to take rather than a side to err on, and it is not a narrowing: `ls-files --cached` lists every tracked path, not what changed, so the index is not a delta but the whole of what the commit will carry. What this costs is the case L0219 cited in its own defence — a preamble edit staged over an entry removed from the index is no longer caught under the flag — and that case is not a loss: the commit carries no such file, so it has no frozen region in it to hold, and a bare run, which is about the working tree, still catches the edit.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
