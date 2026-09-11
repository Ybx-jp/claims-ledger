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

- 2026-09-08T14:43:43-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_history" @34f416118e10a14169475fe23d3176d347d0ed8d
  artifact: 3ebabaa4d367b5f9fa08dd065da0555734c20f01
  note: propagated from a moved ground

- 2026-09-08T15:10:00-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_history" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  note: read against commit 2a76453, which moved the citing comment for this claim into the section its ground names, or out of a section it did not; the code in this section is byte-identical at the pin and at that commit once comments and docstrings are set aside, so nothing the claim rests on changed
- 2026-09-11T03:10:33-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/validate.py § "check_history" @2a76453ef9550e0e7ee13d7cdbcf942282507e6b
  artifact: sha256:a0f5460dc7e6805f42f37f08c07a994eaac5dd9d160914c883daecf28f17db9b
  note: propagated from a moved ground
- 2026-09-11T03:10:33-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/validate.py § "check_history" =sha256:a0f5460dc7e6805f42f37f08c07a994eaac5dd9d160914c883daecf28f17db9b
  note: read against the working tree after the only edit to check_history since the reading at 2a76453, a comment naming the audit file by its path docs/audits/ARCH-AUDIT.md instead of by its bare name: the edges are still every revision against each of its parents plus HEAD against the loaded text, each held to a block-for-block prefix; the assertion holds as written.

## References

- src/claims_ledger/validate.py · standing · cites-as-live
- docs/OPERATING.md · standing · cites-as-live
