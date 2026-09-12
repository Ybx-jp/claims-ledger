---
id: L0219-the-entries-under-cached-are-the-ones-the-index-holds
kind: claim
stated: 2026-09-11T17:51:21-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 1195dfc7987f8b75ea595afd7f9675c5d83eed329d6909d90f3bc53cc23d7854
---

## Assertion

A run asked for the index draws its list of entries from the index as well as from the working tree, so an entry the commit carries is on the list whether or not the tree still has it.

## Scope

metric: which trees the list of entries under `--cached` is drawn from
cohort: every checker run given the cached flag
condition: what each entry then says is read by the loader's existing rule, index first

## Grounds

- code: src/claims_ledger/schema.py § "index_entry_files" =sha256:9762e74dc2e4c302862e676dbc0da6f71dff7f73ecfbf7758ee4c38bff807910
- code: src/claims_ledger/schema.py § "load_entries" =sha256:49e800f46f19dfb2800789a841fb93c451a38e279b0898bfcaf52716fdd4a517

## Warrant

Which entries exist is a question about a tree, and under the flag the tree is the index. The listing was the working tree's whatever the flag said, so an entry staged and then deleted from the tree was in the commit and on no checker's list: measured, all five report a clean run over it, and with that the only entry they report over zero entries — a pass for a check that did not happen, which is the one report this tool must never produce. The index is asked with one ls-files for the whole ledger, so the count of git processes stays flat as the ledger grows. The list is the union of the two trees rather than the index alone, because the other end was already decided here: an entry taken out of the index with git rm --cached and then edited is caught under the flag because the loader still sees it. Checking an entry the commit will not carry costs a report nobody needed; not checking one it will carry is the false pass, so the union is the side to err on.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
