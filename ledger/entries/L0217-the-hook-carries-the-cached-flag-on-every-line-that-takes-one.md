---
id: L0217-the-hook-carries-the-cached-flag-on-every-line-that-takes-one
kind: claim
stated: 2026-09-11T16:06:17-07:00
author: main
grade: measured
verbatim_change: the assertion loses its consequence clause entirely, and the condition now says that what a checker does with the flag is that checker's own claim; Backing unchanged
supersedes: L0216-the-hook-asks-the-index-of-every-checker-that-takes-the-flag
verbatim_sha: 776b95da6b1c54ae146e68a3ebf5c13faaf77a40d26e12407f5abb822dad941c
---

## Assertion

The installed hook carries the cached flag on every checker line whose checker takes one, and on no other line.

## Scope

metric: which of the hook's checker lines carry the cached flag
cohort: the pre-commit hook this command installs
condition: what a checker then does with the flag is that checker's own claim, not this one; how many lines carry it is read off the template rather than fixed here

## Grounds

- code: src/claims_ledger/cli.py § "HOOK_TEMPLATE" =sha256:64ff75703d6e7dc76ef58f6a949f2a473b9a5898b0f825c3d801f012c5e64407

## Warrant

The template runs the entry validator, the pointer resolver and the freshness checker with the cached flag, and the remaining two bare, which is what the template says beside them. Two predecessors went on to state what that buys — first that a drift staged and then reverted cannot commit unreported, then that what those checkers report is what the commit will carry — and both are false, because the two checkers without the flag read the working tree and so does the resolver for a ground pinned at working, which the freshness checker passes over entirely. Neither consequence was decided by this ground: the template settles which lines carry the flag and nothing else, and a claim is worth only what its ground can settle. What the hook buys is stated in the template beside the lines, where a reader of the installed file can weigh it, rather than asserted here where the evidence cannot reach it.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References
- src/claims_ledger/cli.py · standing · cites-as-live
