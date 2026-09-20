---
id: L0054-the-propagation-author-is-one-of-the-verdict-authors
kind: claim
stated: 2026-09-08T02:13:06-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 3b96c5313e927973fda81e19907da5f28a26f480f1c2dfb3cde9d932b9b19843
---

## Assertion

A configuration whose propagation author is outside its list of verdict authors is refused.

## Scope

metric: the outcome of naming a propagation author the verdict-author list does not carry
cohort: the propagation-author and verdict-authors settings
condition: the machinery attributes appended verdicts to the propagation author

## Grounds

- code: src/claims_ledger/config.py § "from_table" @72ad99b4a138640f009ee09b911c741f84776135

## Warrant

from_table tests membership and raises with both values named. Every verdict propagate and freshness append is attributed to the propagation author, so a configuration that leaves it outside the accepted authors is one where the machinery's own writes would be rejected by the validator the moment they landed — a failure that would otherwise appear as a broken checker rather than as the misconfiguration it is.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-08T14:43:42-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" @72ad99b4a138640f009ee09b911c741f84776135
  artifact: ddafd109dfd34f6f75aed2b26773ec283ee64d71
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed
- 2026-09-11T03:10:01-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  artifact: sha256:68ac3fee3de92f6a488946f8b0d0e81b3ce87100281630f31c69300920ed40a3
  note: propagated from a moved ground
- 2026-09-11T03:10:01-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:68ac3fee3de92f6a488946f8b0d0e81b3ce87100281630f31c69300920ed40a3
  note: read against the working tree after from_table gained, since the reading at 2a76453, a check that `citation-placement` is one of its three outcomes and passes it into Config: the membership test of the propagation author in the verdict authors and its error are unchanged; the assertion holds as written.
- 2026-09-14T19:21:53-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:68ac3fee3de92f6a488946f8b0d0e81b3ce87100281630f31c69300920ed40a3
  artifact: sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67
  note: propagated from a moved ground

- 2026-09-14T19:22:21-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67
  note: re-read after the commit that adds the `merge-renumber` key. The propagation author is still read against the verdict authors in the same comparison; nothing about either list moved.
- 2026-09-14T20:21:09-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:d46a203a53a75db2dc9e6de29e3ccfbfa9ea1402096166bf293a295d5d09af67
  artifact: sha256:222a65392276c0cc61e35fec1bfabd395dee5590c848b57d4303b30b4f3ec738
  note: propagated from a moved ground

- 2026-09-14T20:21:11-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:222a65392276c0cc61e35fec1bfabd395dee5590c848b57d4303b30b4f3ec738
  note: re-read after the commit that fixes what the pre-merge gate found. The section lost a verbatim duplicate of the merge-renumber check, which had been written into it twice; the propagation author is still read against the verdict authors.
- 2026-09-20T12:55:57-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:222a65392276c0cc61e35fec1bfabd395dee5590c848b57d4303b30b4f3ec738
  artifact: sha256:8b9600914ff906530f6bf2a48e847507f6edc4fd0eea1ebb2d9aae3f7294d2f5
  note: propagated from a moved ground

- 2026-09-20T12:56:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/config.py § "from_table" =sha256:8b9600914ff906530f6bf2a48e847507f6edc4fd0eea1ebb2d9aae3f7294d2f5
  note: re-read after the commit that adds the `citation-slug` key. The section gained one more check, written like the two beside it and placed after them. The propagation-author check is untouched.


## References

- src/claims_ledger/config.py · standing · cites-as-live
