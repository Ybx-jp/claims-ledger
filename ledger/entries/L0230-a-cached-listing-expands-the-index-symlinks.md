---
id: L0230-a-cached-listing-expands-the-index-symlinks
kind: claim
stated: 2026-09-12T14:45:41-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: a94206a75c5e412e7808c630627d1f454668a4259decb808d273b1c9f5492ef8
---

## Assertion

A listing taken from the index expands the symlinks the index itself holds, so a path a checkout of that index would make reachable is on the list even where no blob is named at it.

## Scope

metric: which paths a cached listing of entries or of documents holds
cohort: every checker run given the cached flag, in a ledger with a repository of its own
condition: a symlink whose target is absolute, climbs out of the repository, or is not reached is not followed, and stays a symlink the mode check names

## Grounds

- code: src/claims_ledger/schema.py § "index_tree" =sha256:89f5d7588165b756bf765224678d6076d17ca59bdb736427aefe120064802d1a
- code: src/claims_ledger/schema.py § "_link_target" =sha256:0d6030595150c23e8db5f8f765de2cb92bed0bae575e21c53bbbd8471f4dd625
- entry: L0231-a-listing-that-fell-back-is-named-by-the-guard · distinguishes

## Warrant

The index is not the set of paths a commit makes reachable, and taking it for that set is how the listing that closed one false pass opened two. `ls-files` reports a symlinked directory as one blob and its target's files as others; a checkout restores the link, and `docs/bad.md` is then a real path git never named. Measured both ways round: with `docs -> real` and `real/bad.md` carrying a citation of an id nothing minted, `references --cached` reported `0 documents` and `0 failure(s)` at exit 0 while a fresh clone of that very commit failed at exit 1 naming the document — the contrast the cached listing exists to close, pointed backwards. With `ledger/entries` a symlink, the entry listing filtered git's real paths against a lexical prefix and matched nothing, so every checker reported `0 entries` at exit 0 where the bare run read one. Both were found by the fix-review gate on this branch (qe ticket 45909368c43c4379, F1 and F3), and both had been covered until this branch by the working-tree listing the index one replaced. The expansion asks the working tree for nothing, which is what keeps the answer the index's own: a symlink's blob is its target, so the whole shape is readable from the commit being built. A link to a regular file takes that file's mode, because `os.path.isfile` follows it and the tree listing therefore counts it as a document; leaving it a symlink made the two listings report one file at different addresses. Bounded on both axes, since a symlink graph is arbitrary: a fixed number of passes, so a cycle stops rather than lengthening paths forever, and a cap on paths added, so a wide fan-out cannot make the listing the slow part of a commit.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-12T15:32:09-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "index_tree" =sha256:0b0d42321267f4a85d06bcb2be38061a789ab184f26542e5ac198bbd3c987dd8
  note: the Assertion stands and three corrections ride with it, all from the fix-review gate on this branch (qe ticket f868273f36b448ab). The cap compared the WHOLE listing against a limit meant for paths added, so a repository with more tracked files than the limit expanded nothing, silently — measured at 4206 files, `0 documents` and `0 failure(s)` at exit 0; this repository's 784 sat under it and said nothing. It counts what it adds now, and reaching either bound returns a reason rather than a short listing. The Warrant's "asks the working tree for nothing" was true of this section alone and false of the listing's effect, because the readers still asked for the invented address and fell back to the tree; L0232 is that rule and it is true again. And the Scope condition's "the mode check names" describes the document listing: on the entries side an unfollowed symlink is named by `validate` instead — measured, a dangling entry symlink stops the bare run at exit 2 and fails the cached run at exit 1, so it is loud either way and nothing passes quietly.

## References

- src/claims_ledger/schema.py · standing · cites-as-live
