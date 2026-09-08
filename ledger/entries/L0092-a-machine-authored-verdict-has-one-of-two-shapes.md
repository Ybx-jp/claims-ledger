---
id: L0092-a-machine-authored-verdict-has-one-of-two-shapes
kind: claim
stated: 2026-09-08T02:30:57-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 5e4c95790de850c706a091ec6ba16e567d17966df9a774655262a4eab5a3b0fc
---

## Assertion

A verdict written under the propagation author is refused unless it takes one of the two shapes the machinery produces.

## Scope

metric: whether a hand-written verdict under the machine's author name is reported
cohort: verdicts whose author is the configured propagation author
condition: the two shapes are propagate's entry evidence and freshness's pinned ground

## Grounds

- code: src/claims_ledger/validate.py § "check_verdicts" @34f416118e10a14169475fe23d3176d347d0ed8d

## Warrant

check_verdicts recognizes contested with entry evidence acting fallen or challenges, and contested with an evidence ground carrying a pin; anything else under that author fails. Those two are what propagate and freshness write. A verdict of any other shape under the machine's name is a person claiming a check that did not run, and a reader takes a machine-authored verdict as exactly that claim.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/validate.py · standing · cites-as-live
