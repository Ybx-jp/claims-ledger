---
id: L0232-an-index-read-names-the-path-the-index-holds
kind: claim
stated: 2026-09-12T15:31:53-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: e3fb10b97d860887272c8ab4a76143ef30f27901d453c04d7ef7e43fc5c1fc62
---

## Assertion

Every read a cached run makes of the index asks for the path the index holds, which for an address the symlink expansion invented is the path that address finally names.

## Scope

metric: which object name a cached read asks git for, given a path from the project root
cohort: every read of the index in a run given the cached flag — the entry blobs, the document bodies, an evidence pointer, and the frozen-region comparison
condition: a path the expansion does not know is asked for as itself, which is every path in a repository holding no symlinks

## Grounds

- code: src/claims_ledger/schema.py § "index_spec" =sha256:69c45e197f4978c0ff0de01cd2afabf5d04bd9ef4641b133274955f5da4a85cc
- code: src/claims_ledger/schema.py § "index_reach" =sha256:0ed75be30c8e0885ab9d0a9b1c28a465347d7d4cc628c3a73991e18954c47a06

## Warrant

Expanding the index's symlinks made the listings name paths git has no blob at, and every reader still asked for the address. `cat-file` answers `missing`, `blob_absent` reads missing as "the index does not hold this", and the reader falls back to the working tree — at exactly the paths the expansion existed to add. So the listing was repaired and the read was left pointing at the wrong tree, which is the same false pass one layer down. Measured: an entry staged with `grade: bogus` under a symlinked entries directory and corrected in the working tree gave `validate --cached` `1 entry` and `0 failure(s)` at exit 0, while a fresh clone of the commit it made failed at exit 1 naming the grade. Worse for a symlink to a file, where git does answer at the address — with the link's own blob, whose bytes are the target's name, so a document's text was the string `note-001.md`. Found by the fix-review gate on this branch (qe ticket f868273f36b448ab). One function rather than a repair at each of the six sites that build an index object name, because a rule written out six times is a rule five of them can drift from, and the count of readers is what made the first fix miss: the listings were the visible half.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-12T16:00:57-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "index_spec" =sha256:69c45e197f4978c0ff0de01cd2afabf5d04bd9ef4641b133274955f5da4a85cc
  note: the Assertion was FALSE when written and is true now. The Warrant counts six sites that build an index object name; there are seven — `resolve.py`'s `digest_in_tree` asks `git show :<target>` directly and was not routed (the fix-review gate on this branch (qe ticket 7b317b5ea95e4670)). Its direction was a false FAIL rather than a false pass, so nothing landed wrong, but the claim said every read and one read was not. Routed now. The enumeration that finds all seven is `grep git_env(index=` — ten call sites, three of which need no path — rather than grepping for the spec shape, which is what missed it.

- 2026-09-12T16:01:20-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "index_reach" =sha256:bd3ede747afafeb7d1bba9e732d1d60d08bd21f82ad280875e5497dbfa119566
  note: acknowledged: a truncated expansion is carried as a note beside the reach rather than as a `why`, so the listing keeps what it reached (L0230's reading). What this claim says an index read names is unchanged.

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- src/claims_ledger/validate.py · standing · cites-as-live
- src/claims_ledger/freshness.py · standing · cites-as-live
- src/claims_ledger/resolve.py · standing · cites-as-live
