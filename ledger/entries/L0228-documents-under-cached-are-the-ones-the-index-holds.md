---
id: L0228-documents-under-cached-are-the-ones-the-index-holds
kind: claim
stated: 2026-09-12T13:56:18-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: b360159f16a12e95cb69d6ac8d6a97d07a767f4cbecc3bcb3b656a649a3d09a2
---

## Assertion

A run asked for the index draws its list of configured documents from the index, so the documents it reads and counts are the ones the commit will carry.

## Scope

metric: which tree the list of configured documents is drawn from under `--cached`
cohort: every checker run given the cached flag, in a ledger with a repository of its own
condition: an index that cannot be asked falls back to the working tree's listing, which the guard already reports

## Grounds

- code: src/claims_ledger/schema.py § "index_documents" =sha256:d87ac9066f902e08294ff79b52fc7c5b2dc16dad983fb9b28f26d82f1e1296f2
- code: src/claims_ledger/schema.py § "selects_document" =sha256:7c7edb7d3387087dc37ee4e2b87ad85991b83773cc3b6b9ec1e16095923f346e
- code: src/claims_ledger/schema.py § "open_ledger" =sha256:70b3e3cbee850df8d4722e811dc047366be795fcf3a117d64116a9c3330dfdde

## Warrant

Which documents exist is a question about a tree, and under the flag the tree is the index. This was not a cached-blind read like the ones around it but a list that never asked: `tree_documents` globs the working tree and is the document universe for every run, so a document the index holds and the tree does not — staged and then removed, as `git add docs/bad.md && rm docs/bad.md` leaves it — was on nobody's list. Not merely unchecked: uncounted, so nothing in the report hinted it existed. Measured in a throwaway repository with such a document carrying a citation of an id nothing minted, `check --cached` reports `1 document` and `0 failure(s)` at exit 0, and a fresh clone of the commit it was about to make fails `references` at exit 1 naming that document. The index is asked with one `ls-files` for the whole repository, so the count of git processes stays flat as the project grows, and the matching is done here rather than through a pathspec because git's `:(glob)` is close to `glob`'s and not the same — a pathspec narrower anywhere is a document dropped without a word. The one rule `glob` applies that a list of strings does not carry is the dotfile rule, so `selects_document` applies it, and a test holds the two listings to the same answer over a tree built to exercise the edges.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-12T14:47:27-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "index_documents" =sha256:0baee22ce9f04a61c4275aeec57091962013844a40efbfc1abe7fb9b1041617b
  note: the Assertion stands and the listing now expands the index's own symlinks to reach it. One clause of the Warrant was false as written: "the index ... is what the commit will carry" is not true of a committed symlinked directory, where `ls-files` names the link and its target's files and a checkout makes a third path real. Measured by the fix-review gate on this branch (qe ticket 45909368c43c4379), F3 — `docs -> real` with `real/bad.md` gave `0 documents` at exit 0 while a fresh clone of the commit failed at exit 1. Repaired in code rather than by supersession, the way this ledger has settled a false Warrant clause before; L0230 states the rule.

- 2026-09-12T14:48:18-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/schema.py § "open_ledger" =sha256:69a9b396207e4ba4ed6f2a4c9f494d0ca338570b2270afb81197d311523e2f2b
  note: the other half of the same reading. `open_ledger` carries the listing's `why` out now instead of dropping it, so a fallback is named rather than silent; the rule is L0231's and this claim is unchanged by it.

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- src/claims_ledger/cli.py · standing · cites-as-live
