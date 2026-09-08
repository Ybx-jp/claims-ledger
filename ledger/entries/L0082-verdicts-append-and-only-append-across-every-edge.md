---
id: L0082-verdicts-append-and-only-append-across-every-edge
kind: claim
stated: 2026-09-08T02:30:45-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 6a66d5e7fed149e0794fc87ee6762eb528aa5da58dae0509b67cb6816ee0a1d2
---

## Assertion

Verdicts append and only append, checked along every edge of the entry's history: each revision against each of its parents, and the loaded text against HEAD.

## Scope

metric: which pairs of revisions the append-only comparison runs over
cohort: committed entries with any number of revisions
condition: the working tree, or the index under --cached, is the last thing compared

## Grounds

- code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_history builds its edges from the walk — every revision paired with each of its parents — and adds the edge from HEAD to the text that was loaded. Along each edge the older side's verdict blocks must be a prefix of the newer side's, block for block, and one changed or removed is reported by its index. Comparing only the tip against the revision before it would let an edit that landed mid-history and was undone at the tip pass unseen; walking the edges is what makes a commit that bypassed the hook catchable by the next run anywhere.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
