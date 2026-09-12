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

- 2026-09-12T14:47:27-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "index_entry_files" =sha256:a37ddd186d31e632203734cdeb652380a483c34a4a265e9876e55d716da780a7
  note: the Assertion stands. The same false clause as L0228 carries here, and two defects the union had been covering came with it: a symlinked `ledger/entries` gave `0 entries` at exit 0 where the bare run read one, and dropping the union's `set()` loaded an unmerged entry once per stage — 3 entries and 24 failures where 1 and 8 were due. Both measured by the fix-review gate on this branch (qe ticket 45909368c43c4379), F1 and F4; the listing expands symlinks and keys by the path each address finally names.

- 2026-09-12T15:32:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "index_entry_files" =sha256:0c0f0e36f6f6f7747c0fed9d5555396c6c78451f8805b44b8f98a996ad0cb34b
  note: acknowledged: the listing reads the shared expansion rather than asking for its own (L0232). The list itself is unchanged.

- 2026-09-12T15:32:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "load_entries" =sha256:1f07291798534700d0b4b32f58be6faa647da05854f6a8b9dee242dbcfb99ab2
  note: acknowledged: the entry blobs are asked for at the path the index holds (L0232). Which entries the list holds is unchanged.

## References

- src/claims_ledger/schema.py · standing · cites-as-live
