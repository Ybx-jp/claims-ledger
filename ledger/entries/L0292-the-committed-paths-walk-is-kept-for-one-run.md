---
id: L0292-the-committed-paths-walk-is-kept-for-one-run
kind: claim
stated: 2026-09-20T15:23:31-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 4ead6bbff5178595c12018995534fc35d0f4ac0c4c9f6ac860a5d87a6cd07098
---

## Assertion

The walk that lists what a repository holds is made once per pathspec for the length of a run, and is kept on the ledger rather than outliving it.

## Scope

metric: the number of history walks a run makes to answer whether entries are committed
cohort: a run of any checker over a ledger of any size
condition: the question is asked once, or once per entry

## Grounds

- code: src/claims_ledger/schema.py § "committed_paths" =sha256:c7edfaea53cbbb45d45a53598f842719fe0e3e8be90964eaec499d8b42165a96
- code: src/claims_ledger/schema.py § "heads_in_progress" =sha256:9779a326ae670a1e6419a44734a968cead7b88808057bafaf7b0639da9b9edcb

## Warrant

The question is asked once per entry and answered from one walk of the entries directory, so the process count stays flat as the ledger grows — a walk apiece is the shape that took a thousand-entry check to five minutes, and it is the shape a per-entry lookup falls back into the moment the lookup stops being a single cheap command. Kept on the ledger and not in a module-level cache keyed by repository: the tests drive the CLI in this process and interleave commits with checks, so a cache that outlived a run would answer a later question from a history that had moved, and the suite would pass on an answer that was wrong.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
